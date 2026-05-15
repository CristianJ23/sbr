from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List, Optional
from expert_system.engine import DidacticEngine, Rule
from expert_system.rules_data import REGLAS_TURISMO, PREFERENCIAS_TURISMO
import logging

# Configuración de logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SBR Didáctico para Turismo")

# Archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Estado global (en memoria para este prototipo)
current_rules = list(REGLAS_TURISMO)
custom_facts = [] # Lista de {"id": str, "label": str, "desc": str}

class TourismRequest(BaseModel):
    preferences: List[str]

class GoalRequest(BaseModel):
    goal: str
    facts: List[str]

class NewRuleRequest(BaseModel):
    name: str
    logic: str
    conditions: List[str]
    conclusions: List[str]
    explanation: str
    priority: int = 0

class NewFactRequest(BaseModel):
    id: str
    label: str
    desc: Optional[str] = ""

def get_all_facts():
    # Hechos base
    facts_dict = {p["id"]: {"label": p["label"], "desc": p.get("desc", ""), "type": "base"} for p in PREFERENCIAS_TURISMO}
    
    # Hechos personalizados
    for f in custom_facts:
        facts_dict[f["id"]] = {"label": f["label"], "desc": f.get("desc", ""), "type": "custom"}
        
    # Hechos deducibles de reglas que no estén ya
    for rule in current_rules:
        for conc in rule.conclusions:
            if conc not in facts_dict:
                facts_dict[conc] = {
                    "label": conc.replace("_", " ").title(),
                    "desc": "Hecho deducido por reglas.",
                    "type": "inferred"
                }
    
    return [{"id": k, **v} for k, v in facts_dict.items()]

@app.get("/")
async def read_root(request: Request):
    all_facts = get_all_facts()
    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={
            "facts": all_facts,
            "rules": current_rules
        }
    )

@app.post("/diagnose")
async def diagnose(request: TourismRequest):
    # Usar las reglas actuales para el motor de inferencia
    engine = DidacticEngine(current_rules)
    result = engine.infer(set(request.preferences))
    return result

@app.post("/verify_goal")
async def verify_goal(request: GoalRequest):
    engine = DidacticEngine(current_rules)
    result = engine.verify_goal(request.goal, set(request.facts))
    return result

@app.post("/add_fact")
async def add_fact(fact: NewFactRequest):
    if not any(f["id"] == fact.id for f in custom_facts):
        custom_facts.append({"id": fact.id, "label": fact.label, "desc": fact.desc})
    return {"status": "success", "all_facts": get_all_facts()}

@app.post("/add_rule")
async def add_rule(rule_req: NewRuleRequest):
    new_id = f"R{len(current_rules) + 1}"
    
    # Extraer el label de la conclusión si es posible (asumimos que script.js envía el label en un campo extra o lo inferimos)
    # Para ser más robustos, vamos a registrar la conclusión como un hecho personalizado si no existe
    # Nota: El request NewRuleRequest no tenía label de conclusión separado, pero podemos inferirlo de la lógica o ampliar el modelo.
    # Vamos a ampliar el modelo NewRuleRequest para que sea más explícito.
    
    new_rule = Rule(
        id=new_id,
        name=rule_req.name,
        logic=rule_req.logic,
        conditions=rule_req.conditions,
        conclusions=rule_req.conclusions,
        explanation=rule_req.explanation,
        priority=rule_req.priority
    )
    current_rules.append(new_rule)
    
    # Registrar conclusiones como hechos si no existen
    for conc in rule_req.conclusions:
        if not any(f["id"] == conc for f in PREFERENCIAS_TURISMO) and not any(f["id"] == conc for f in custom_facts):
            # Usar un label genérico si no lo tenemos, o podemos pedirlo. 
            # Por ahora, usamos el ID formateado.
            label = conc.replace("_", " ").title()
            custom_facts.append({"id": conc, "label": label, "desc": "Deducido por regla personalizada."})

    return {"status": "success", "rule": new_rule, "all_facts": get_all_facts()}

@app.post("/reset_rules")
async def reset_rules():
    global current_rules, custom_facts
    current_rules = list(REGLAS_TURISMO)
    custom_facts = []
    return {"status": "success", "all_facts": get_all_facts()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
