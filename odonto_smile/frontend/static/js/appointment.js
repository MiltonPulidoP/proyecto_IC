document.addEventListener('DOMContentLoaded', function() {
    // Cargar citas al abrir la página
    cargarCitas();
    
    // Manejar envío del formulario
    const form = document.getElementById('appointment-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            fetch(form.action, {
                method: 'POST',
                body: new FormData(form)
            })
            .then(response => {
                if (response.redirected) {
                    window.location.href = response.url;
                } else {
                    return response.json();
                }
            })
            .then(data => {
                if (data && data.success) {
                    cargarCitas();
                    form.reset();
                    // Mostrar mensaje de éxito
                    alert('Cita agendada exitosamente!');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al agendar cita');
            });
        });
    }
});

function cargarCitas() {
    fetch('/obtener_citas')
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return response.json();
        })
        .then(citas => {
            const lista = document.getElementById('appointments-list');
            if (!lista) return;
            
            lista.innerHTML = '';
            
            if (citas.length === 0) {
                lista.innerHTML = '<p class="no-appointments">No tienes citas programadas</p>';
                return;
            }
            
            citas.forEach(cita => {
                const citaElement = document.createElement('div');
                citaElement.className = 'cita-item';
                citaElement.innerHTML = `
                    <div class="cita-header">
                        <h4>${cita.tratamiento}</h4>
                        <span class="cita-sede">${cita.sede}</span>
                    </div>
                    <div class="cita-body">
                        <p><strong>Fecha:</strong> ${formatDate(cita.fecha)} a las ${cita.hora}</p>
                        <p><strong>Paciente:</strong> ${cita.nombres} ${cita.apellidos}</p>
                        <p><strong>Teléfono:</strong> ${cita.telefono || 'N/A'}</p>
                    </div>
                    <button class="btn-cancelar" onclick="cancelarCita(${cita.id})">
                        Cancelar Cita
                    </button>
                `;
                lista.appendChild(citaElement);
            });
        })
        .catch(error => {
            console.error('Error al cargar citas:', error);
            const lista = document.getElementById('appointments-list');
            if (lista) {
                lista.innerHTML = '<p class="error-message">Error al cargar las citas. Intenta recargar la página.</p>';
            }
        });
}

function cancelarCita(id) {
    if (confirm('¿Estás seguro que deseas cancelar esta cita?')) {
        fetch(`/cancelar_cita/${id}`, { 
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        })
        .then(response => {
            if (response.ok) {
                cargarCitas();
                alert('Cita cancelada exitosamente');
            } else {
                throw new Error('Error al cancelar cita');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cancelar la cita');
        });
    }
}

// Función auxiliar para formatear fechas
function formatDate(dateString) {
    if (!dateString) return 'Fecha no definida';
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return new Date(dateString).toLocaleDateString('es-ES', options);
}