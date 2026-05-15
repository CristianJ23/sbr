async function verifyGoal() {
    const goal = document.getElementById('goal-selector').value;
    const checkboxes = document.querySelectorAll('input[name="preference"]:checked');
    const selectedFacts = Array.from(checkboxes).map(cb => cb.value);
    
    if (!goal) {
        alert("Por favor, selecciona una meta de la lista.");
        return;
    }

    const statusBox = document.getElementById('goal-result-status');
    statusBox.innerHTML = '<p class="loading-msg">Procesando búsqueda recursiva...</p>';

    try {
        const response = await fetch('/verify_goal', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ goal: goal, facts: selectedFacts })
        });
        
        const data = await response.json();
        
        // Renderizar logs y pasos
        renderInference(data);

        // Mostrar status específico de la meta
        statusBox.className = 'goal-status-box ' + (data.goal_reached ? 'success' : 'failure');
        
        let statusHtml = `
            <div class="status-icon">${data.goal_reached ? '✔' : '✖'}</div>
            <div class="status-text">
                <strong>${data.goal_reached ? 'META ALCANZADA' : 'META NO ALCANZADA'}</strong>
        `;

        if (data.goal_reached) {
            statusHtml += `<span>El sistema encontró una ruta lógica con los hechos actuales.</span>`;
        } else if (data.required_facts && data.required_facts.length > 0) {
            // Filtrar hechos que ya tenemos para mostrar solo los faltantes
            const missing = data.required_facts.filter(f => !selectedFacts.includes(f));
            statusHtml += `<span>Faltan estos hechos base: <br><strong>${missing.join(', ')}</strong></span>`;
        } else {
            statusHtml += `<span>No hay reglas ni hechos que lleven a esta meta.</span>`;
        }

        statusHtml += `</div>`;
        statusBox.innerHTML = statusHtml;

    } catch (error) {
        console.error('Error:', error);
        statusBox.innerHTML = '<p class="error">Error al conectar con el motor.</p>';
    }
}

async function startReasoning() {
    const checkboxes = document.querySelectorAll('input[name="preference"]:checked');
    const selectedFacts = Array.from(checkboxes).map(cb => cb.value);
    
    const stepsContainer = document.getElementById('reasoning-steps');
    const resultsContainer = document.getElementById('final-results');
    const consoleOutput = document.getElementById('console-output');

    if (selectedFacts.length === 0) {
        stepsContainer.innerHTML = '<p class="empty-msg">El motor está a la espera de hechos iniciales...</p>';
        resultsContainer.innerHTML = '<div class="result-placeholder">Sin conclusiones aún.</div>';
        return;
    }

    try {
        const response = await fetch('/diagnose', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ preferences: selectedFacts })
        });
        
        const data = await response.json();
        renderInference(data);
    } catch (error) {
        console.error('Error:', error);
    }
}

function renderInference(data) {
    console.log("Datos recibidos del motor:", data);
    const stepsContainer = document.getElementById('reasoning-steps');
    const resultsContainer = document.getElementById('final-results');
    const consoleOutput = document.getElementById('console-output');

    // 1. Limpiar y Actualizar Pasos de Razonamiento
    stepsContainer.innerHTML = '';
    if (!data.steps || data.steps.length === 0) {
        stepsContainer.innerHTML = '<div class="info-alert">Los hechos seleccionados no activaron ninguna regla. Intenta añadir más hechos o crear una regla que coincida.</div>';
    } else {
        data.steps.forEach((step, index) => {
            const stepDiv = document.createElement('div');
            stepDiv.className = 'reasoning-card';
            if (step.conflict_resolved) stepDiv.classList.add('conflict-resolved');
            
            stepDiv.style.animationDelay = `${index * 0.2}s`;
            
            let conflictHtml = '';
            if (step.conflict_resolved && step.conflict_info) {
                conflictHtml = `<div class="conflict-info-badge">⚖️ ${step.conflict_info}</div>`;
            }

            stepDiv.innerHTML = `
                <div class="card-header">⚡ Regla Disparada: <strong>${step.rule_name}</strong></div>
                ${conflictHtml}
                <p>${step.reason}</p>
                <div class="inference-tag">DEDUCCIÓN: <span>${step.new_facts.join(', ')}</span></div>
            `;
            stepsContainer.appendChild(stepDiv);
        });
    }

    // 2. Mostrar Conclusiones Finales (Todo lo que no era un hecho inicial)
    resultsContainer.innerHTML = '';
    const initialSet = new Set(data.initial_facts);
    const deductions = data.final_facts.filter(f => !initialSet.has(f));

    if (deductions.length === 0) {
        resultsContainer.innerHTML = '<div class="result-placeholder">No se han generado nuevas deducciones con los hechos actuales.</div>';
    } else {
        deductions.forEach(factId => {
            const badge = document.createElement('div');
            badge.className = 'destination-badge';
            // Intentar embellecer el ID para mostrarlo
            const cleanLabel = factId.replace('destino_', '').replace(/_/g, ' ').toUpperCase();
            badge.innerHTML = `<span>★</span> ${cleanLabel}`;
            resultsContainer.appendChild(badge);
        });
    }

    // 3. Logs de Consola (Debug)
    consoleOutput.innerHTML = '';
    data.logs.forEach(log => {
        const entry = document.createElement('div');
        entry.className = 'log-entry';
        if (log.includes('✔')) entry.classList.add('success');
        if (log.includes('➡')) entry.classList.add('info');
        if (log.includes('---')) entry.style.color = 'var(--gold)';
        entry.innerText = log;
        consoleOutput.appendChild(entry);
    });
    consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

// Lógica para añadir reglas
document.getElementById('rule-form')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const name = document.getElementById('rule-name').value;
    const conditions = Array.from(document.querySelectorAll('input[name="rule-condition"]:checked')).map(cb => cb.value);
    const conclusionId = document.getElementById('rule-conclusion-id').value;
    const conclusionLabel = document.getElementById('rule-conclusion-label').value;
    const explanation = document.getElementById('rule-explanation').value;
    const priority = parseInt(document.getElementById('rule-priority')?.value || 0);

    if (conditions.length === 0) {
        alert("Selecciona al menos una condición.");
        return;
    }

    // Crear string de lógica visual
    const conditionLabels = Array.from(document.querySelectorAll('input[name="rule-condition"]:checked'))
        .map(cb => cb.parentElement.querySelector('span').innerText);
    const logic = `SI (${conditionLabels.join(' Y ')}) ENTONCES ${conclusionLabel}`;

    const newRule = {
        name,
        logic,
        conditions,
        conclusions: [conclusionId],
        explanation,
        priority
    };

    try {
        const response = await fetch('/add_rule', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newRule)
        });
        const data = await response.json();
        
        if (data.status === 'success') {
            updateUI(data.all_facts, [data.rule]); // En el backend append rules, aquí solo mostramos la nueva o recargamos todo
            // Para ser más simple, recargamos la página o pedimos todas las reglas
            location.reload(); // Recarga simple para actualizar todo el contexto Jinja2
        }
    } catch (error) {
        console.error('Error:', error);
    }
});

async function resetRules() {
    if (!confirm("¿Seguro que quieres resetear todas las reglas personalizadas?")) return;
    
    try {
        await fetch('/reset_rules', { method: 'POST' });
        location.reload();
    } catch (error) {
        console.error('Error:', error);
    }
}

function updateUI(allFacts, newRules) {
    // Esta función podría usarse para actualizar el DOM sin recargar, 
    // pero location.reload() es más seguro para mantener consistencia con Jinja2.
}

document.addEventListener('DOMContentLoaded', () => {
    // Inicialización si es necesaria
});
