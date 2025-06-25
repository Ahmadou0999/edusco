/**
 * JavaScript personnalisé pour l'interface d'administration Edusco
 */

// Initialisation au chargement de la page
document.addEventListener('DOMContentLoaded', function() {
    // Initialiser les tooltips Bootstrap
    $('[data-toggle="tooltip"]').tooltip();
    
    // Initialiser les popovers Bootstrap
    $('[data-toggle="popover"]').popover();
    
    // Initialiser les confirmations de suppression
    initDeleteConfirmations();
    
    // Initialiser les validations de formulaires
    initFormValidations();
    
    // Initialiser les recherches en temps réel
    initRealTimeSearch();
    
    // Initialiser les sélecteurs dynamiques
    initDynamicSelectors();
});

/**
 * Initialise les confirmations de suppression
 */
function initDeleteConfirmations() {
    // Confirmation pour les suppressions
    document.querySelectorAll('[data-confirm]').forEach(function(element) {
        element.addEventListener('click', function(e) {
            const message = this.getAttribute('data-confirm');
            if (!confirm(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
}

/**
 * Initialise les validations de formulaires
 */
function initFormValidations() {
    // Validation des emails
    document.querySelectorAll('input[type="email"]').forEach(function(input) {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    // Validation des dates
    document.querySelectorAll('input[type="date"]').forEach(function(input) {
        input.addEventListener('change', function() {
            validateDate(this);
        });
    });
    
    // Validation des nombres
    document.querySelectorAll('input[type="number"]').forEach(function(input) {
        input.addEventListener('input', function() {
            validateNumber(this);
        });
    });
}

/**
 * Initialise les recherches en temps réel
 */
function initRealTimeSearch() {
    const searchInputs = document.querySelectorAll('.search-input');
    
    searchInputs.forEach(function(input) {
        let timeout;
        
        input.addEventListener('input', function() {
            clearTimeout(timeout);
            const searchTerm = this.value.toLowerCase();
            const table = this.closest('.card').querySelector('table');
            
            if (table) {
                timeout = setTimeout(function() {
                    filterTable(table, searchTerm);
                }, 300);
            }
        });
    });
}

/**
 * Initialise les sélecteurs dynamiques
 */
function initDynamicSelectors() {
    // Sélecteur de semestre pour les UEs
    const semestreSelect = document.getElementById('semestre_id');
    const ueSelect = document.getElementById('unite_enseignement_id');
    
    if (semestreSelect && ueSelect) {
        semestreSelect.addEventListener('change', function() {
            loadUEsBySemestre(this.value, ueSelect);
        });
    }
    
    // Sélecteur d'UE pour les matières
    const matiereUESelect = document.getElementById('unite_enseignement_id');
    const matiereSelect = document.getElementById('matiere_id');
    
    if (matiereUESelect && matiereSelect) {
        matiereUESelect.addEventListener('change', function() {
            loadMatieresByUE(this.value, matiereSelect);
        });
    }
}

/**
 * Valide un email
 */
function validateEmail(input) {
    const email = input.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        input.setCustomValidity('Veuillez entrer un email valide');
        showFieldError(input, 'Email invalide');
    } else {
        input.setCustomValidity('');
        hideFieldError(input);
    }
}

/**
 * Valide une date
 */
function validateDate(input) {
    const date = new Date(input.value);
    const today = new Date();
    
    if (input.value && date > today) {
        input.setCustomValidity('La date ne peut pas être dans le futur');
        showFieldError(input, 'Date invalide');
    } else {
        input.setCustomValidity('');
        hideFieldError(input);
    }
}

/**
 * Valide un nombre
 */
function validateNumber(input) {
    const value = parseFloat(input.value);
    const min = parseFloat(input.min);
    const max = parseFloat(input.max);
    
    if (input.value && (isNaN(value) || (min && value < min) || (max && value > max))) {
        input.setCustomValidity('Valeur invalide');
        showFieldError(input, 'Valeur invalide');
    } else {
        input.setCustomValidity('');
        hideFieldError(input);
    }
}

/**
 * Filtre un tableau selon un terme de recherche
 */
function filterTable(table, searchTerm) {
    const rows = table.querySelectorAll('tbody tr');
    
    rows.forEach(function(row) {
        const text = row.textContent.toLowerCase();
        if (text.includes(searchTerm)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
}

/**
 * Charge les UEs par semestre
 */
function loadUEsBySemestre(semestreId, ueSelect) {
    if (!semestreId) {
        ueSelect.innerHTML = '<option value="">Sélectionner une UE</option>';
        return;
    }
    
    fetch(`/admin/api/ues-par-semestre/${semestreId}`)
        .then(response => response.json())
        .then(data => {
            ueSelect.innerHTML = '<option value="">Sélectionner une UE</option>';
            data.forEach(ue => {
                const option = document.createElement('option');
                option.value = ue.id;
                option.textContent = `${ue.code} - ${ue.nom}`;
                ueSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des UEs:', error);
        });
}

/**
 * Charge les matières par UE
 */
function loadMatieresByUE(ueId, matiereSelect) {
    if (!ueId) {
        matiereSelect.innerHTML = '<option value="">Sélectionner une matière</option>';
        return;
    }
    
    fetch(`/admin/api/matieres-par-ue/${ueId}`)
        .then(response => response.json())
        .then(data => {
            matiereSelect.innerHTML = '<option value="">Sélectionner une matière</option>';
            data.forEach(matiere => {
                const option = document.createElement('option');
                option.value = matiere.id;
                option.textContent = `${matiere.code} - ${matiere.nom}`;
                matiereSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Erreur lors du chargement des matières:', error);
        });
}

/**
 * Affiche une erreur de champ
 */
function showFieldError(input, message) {
    const formGroup = input.closest('.form-group');
    let errorDiv = formGroup.querySelector('.field-error');
    
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'field-error text-danger small mt-1';
        formGroup.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    input.classList.add('is-invalid');
}

/**
 * Cache une erreur de champ
 */
function hideFieldError(input) {
    const formGroup = input.closest('.form-group');
    const errorDiv = formGroup.querySelector('.field-error');
    
    if (errorDiv) {
        errorDiv.remove();
    }
    
    input.classList.remove('is-invalid');
}

/**
 * Affiche une notification toast
 */
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-header">
            <strong class="mr-auto">Notification</strong>
            <button type="button" class="ml-2 mb-1 close" data-dismiss="toast">
                <span>&times;</span>
            </button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;
    
    // Ajouter le toast au conteneur
    let toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toast-container';
        toastContainer.className = 'toast-container position-fixed top-0 end-0 p-3';
        toastContainer.style.zIndex = '9999';
        document.body.appendChild(toastContainer);
    }
    
    toastContainer.appendChild(toast);
    
    // Afficher le toast
    $(toast).toast({
        autohide: true,
        delay: 5000
    }).toast('show');
    
    // Supprimer le toast après fermeture
    $(toast).on('hidden.bs.toast', function() {
        toast.remove();
    });
}

/**
 * Confirme une action
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Formate un nombre
 */
function formatNumber(number, decimals = 2) {
    return parseFloat(number).toFixed(decimals);
}

/**
 * Formate une date
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR');
}

/**
 * Formate une date et heure
 */
function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR');
}

/**
 * Génère un ID unique
 */
function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
}

/**
 * Copie du texte dans le presse-papiers
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        showToast('Texte copié dans le presse-papiers', 'success');
    }).catch(function() {
        showToast('Erreur lors de la copie', 'error');
    });
}

/**
 * Exporte un tableau en CSV
 */
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    const rows = table.querySelectorAll('tr');
    let csv = [];
    
    rows.forEach(function(row) {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        
        cols.forEach(function(col) {
            rowData.push('"' + col.textContent.replace(/"/g, '""') + '"');
        });
        
        csv.push(rowData.join(','));
    });
    
    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    
    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

/**
 * Imprime une section
 */
function printSection(sectionId) {
    const section = document.getElementById(sectionId);
    const printWindow = window.open('', '_blank');
    
    printWindow.document.write(`
        <html>
            <head>
                <title>Impression</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap/4.6.0/css/bootstrap.min.css">
                <style>
                    @media print {
                        .no-print { display: none !important; }
                    }
                </style>
            </head>
            <body>
                ${section.outerHTML}
            </body>
        </html>
    `);
    
    printWindow.document.close();
    printWindow.focus();
    printWindow.print();
    printWindow.close();
}

// Export des fonctions pour utilisation globale
window.EduscoAdmin = {
    showToast,
    confirmAction,
    formatNumber,
    formatDate,
    formatDateTime,
    generateId,
    copyToClipboard,
    exportTableToCSV,
    printSection
}; 