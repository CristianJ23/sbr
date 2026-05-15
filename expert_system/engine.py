from typing import List, Set, Dict, Optional
from pydantic import BaseModel

class Rule(BaseModel):
    id: str
    name: str
    logic: str          # Texto didáctico: "SI A Y B ENTONCES C"
    conditions: List[str]
    conclusions: List[str]
    explanation: str    # Explicación del porqué de esta regla
    priority: int = 0   # Prioridad para resolución de conflictos

class InferenceStep(BaseModel):
    rule_name: str
    reason: str
    new_facts: List[str]
    conflict_resolved: bool = False
    conflict_info: Optional[str] = None

class InferenceResult(BaseModel):
    initial_facts: List[str]
    final_facts: List[str]
    applied_rules: List[Rule]
    steps: List[InferenceStep]
    logs: List[str]
    goal_reached: Optional[bool] = None
    required_facts: Optional[List[str]] = None  # Hechos base necesarios encontrados

class DidacticEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def infer(self, initial_facts: Set[str]) -> InferenceResult:
        """Inferencia hacia adelante con Resolución de Conflictos"""
        working_memory = set(initial_facts)
        applied_rules = []
        steps = []
        logs = []
        
        logs.append(f"● [FORWARD] Iniciando con: {list(initial_facts)}")
        
        changed = True
        cycle = 1
        while changed:
            changed = False
            logs.append(f"--- Ciclo de Razonamiento #{cycle} ---")
            
            # 1. Identificar Conjunto de Conflicto (Conflict Set)
            conflict_set = []
            for rule in self.rules:
                if rule.id in [r.id for r in applied_rules]: continue
                if all(cond in working_memory for cond in rule.conditions):
                    conflict_set.append(rule)
            
            if not conflict_set:
                logs.append("● No hay más reglas para activar. Proceso terminado.")
                break

            # 2. Resolución de Conflictos
            # Estrategia: 
            #   1. Mayor Prioridad (explicit weight)
            #   2. Especificidad (la que más "SI" tuvo / más condiciones) - Pedido por el usuario
            #   3. Orden de definición (ID)
            
            if len(conflict_set) > 1:
                logs.append(f"⚠ CONFLICTO: {len(conflict_set)} reglas activadas simultáneamente.")
                # Ordenar por prioridad descendente, luego por número de condiciones descendente
                conflict_set.sort(key=lambda r: (r.priority, len(r.conditions), r.id), reverse=True)
                
                selected_rule = conflict_set[0]
                resolution_reason = f"Resolución: Se eligió '{selected_rule.name}' por mayor especificidad ({len(selected_rule.conditions)} condiciones) y prioridad ({selected_rule.priority})."
                logs.append(f"   ✓ {resolution_reason}")
                is_conflict = True
            else:
                selected_rule = conflict_set[0]
                resolution_reason = None
                logs.append(f"✔ Regla ACTIVADA: {selected_rule.name}")
                is_conflict = False

            # 3. Disparar la regla seleccionada
            new_findings = [c for c in selected_rule.conclusions if c not in working_memory]
            
            # Siempre marcamos como aplicada para no volver a considerarla
            applied_rules.append(selected_rule)
            
            if new_findings:
                for c in new_findings: working_memory.add(c)
                steps.append(InferenceStep(
                    rule_name=selected_rule.name, 
                    reason=selected_rule.explanation, 
                    new_facts=new_findings,
                    conflict_resolved=is_conflict,
                    conflict_info=resolution_reason
                ))
                logs.append(f"➡ Se dedujo: {new_findings}")
                changed = True
            else:
                logs.append(f"ℹ La regla {selected_rule.name} no aportó nuevos hechos.")
                # Seguimos buscando otras reglas en el siguiente ciclo
                changed = True 

            cycle += 1
            
        return InferenceResult(initial_facts=list(initial_facts), final_facts=list(working_memory), applied_rules=applied_rules, steps=steps, logs=logs)

    def verify_goal(self, goal: str, facts: Set[str]) -> InferenceResult:
        """Encadenamiento hacia atrás con análisis de requisitos"""
        logs = []
        steps = []
        applied_rules = []
        working_memory = set(facts)
        visited_goals = set()
        all_required_primitives = set()

        logs.append(f"● [BACKWARD] Analizando requisitos para meta: '{goal}'")

        def prove(target: str, depth: int = 0) -> bool:
            indent = "  " * depth
            logs.append(f"{indent}? Evaluando meta: {target}")
            
            if target in working_memory:
                logs.append(f"{indent}✔ '{target}' ya está presente en la memoria.")
                return True
            
            if target in visited_goals:
                return False
            
            visited_goals.add(target)
            
            matching_rules = [r for r in self.rules if target in r.conclusions]
            
            if not matching_rules:
                logs.append(f"{indent}ℹ '{target}' es un hecho base necesario.")
                all_required_primitives.add(target)
                return False
            
            # Intentar probar por reglas
            success_with_any_rule = False
            for rule in matching_rules:
                logs.append(f"{indent}🔍 Analizando Regla: {rule.name}")
                
                rule_satisfied = True
                for cond in rule.conditions:
                    if not prove(cond, depth + 1):
                        rule_satisfied = False
                        # No hacemos break para descubrir TODOS los hechos base necesarios
                
                if rule_satisfied:
                    logs.append(f"{indent}✔ La Regla {rule.name} puede satisfacer '{target}'.")
                    if target not in working_memory:
                        working_memory.add(target)
                        applied_rules.append(rule)
                        steps.append(InferenceStep(
                            rule_name=rule.name,
                            reason=f"Para deducir {target}, se requiere validar {rule.conditions}",
                            new_facts=[target]
                        ))
                    success_with_any_rule = True
                    break # Si una regla funciona, esta meta es alcanzable
            
            return success_with_any_rule

        goal_attained = prove(goal)
        
        logs.append(f"● Análisis completado.")
        if goal_attained:
            logs.append("✔ La meta se puede alcanzar con los hechos actuales.")
        else:
            logs.append(f"✖ Se requieren hechos adicionales: {list(all_required_primitives)}")

        return InferenceResult(
            initial_facts=list(facts),
            final_facts=list(working_memory),
            applied_rules=applied_rules,
            steps=steps,
            logs=logs,
            goal_reached=goal_attained,
            required_facts=list(all_required_primitives)
        )
