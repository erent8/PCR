/**
 * PCR Optimizer - Ana JavaScript Dosyası
 */

document.addEventListener('DOMContentLoaded', function() {
    
    // Formların doğrulanması için Bootstrap validation
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    // Tooltip'leri başlat
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
    
    // Primer dizilerini büyük harfe çevirme
    const primerInputs = document.querySelectorAll('textarea[name^="primer"], textarea[name="sequence"]');
    
    primerInputs.forEach(input => {
        input.addEventListener('blur', function() {
            // DNA dizisini büyük harfe çevir
            this.value = this.value.toUpperCase();
            
            // Boşlukları ve geçersiz karakterleri temizle
            this.value = this.value.replace(/[^ATCG]/g, '');
        });
    });
    
    // Optimize Edici sayfasında indirme butonları
    setupDownloadButtons();
    
    // GC içeriği göstergeleri için renk kodlaması
    setupGCContentIndicators();
});

/**
 * İndirme butonlarını ayarla
 */
function setupDownloadButtons() {
    const downloadButtons = {
        'downloadText': 'text',
        'downloadJSON': 'json', 
        'downloadCSV': 'csv'
    };
    
    for (const [buttonId, format] of Object.entries(downloadButtons)) {
        const button = document.getElementById(buttonId);
        if (button) {
            button.addEventListener('click', function() {
                downloadProtocol(format);
            });
        }
    }
}

/**
 * Protokolü farklı formatlarda indirmek için
 */
function downloadProtocol(format) {
    const protocolElement = document.getElementById('protocolData');
    
    if (!protocolElement) {
        console.error('Protocol data not found');
        return;
    }
    
    const protocol = JSON.parse(protocolElement.dataset.protocol);
    
    fetch('/download_protocol', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            protocol: protocol,
            format: format
        })
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Protokol indirme işlemi başarısız oldu.');
    })
    .then(blob => {
        // İndirme işlemi için bir link oluşturup tıklama
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        const extension = format === 'json' ? 'json' : (format === 'csv' ? 'csv' : 'txt');
        a.href = url;
        a.download = `pcr_protokolu.${extension}`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
    })
    .catch(error => {
        console.error('Hata:', error);
        alert('Protokol indirme sırasında bir hata oluştu: ' + error.message);
    });
}

/**
 * GC içeriği göstergeleri için renk kodlaması uygula
 */
function setupGCContentIndicators() {
    const gcIndicators = document.querySelectorAll('.gc-indicator');
    
    gcIndicators.forEach(indicator => {
        const gcValue = parseFloat(indicator.dataset.gcContent || 0);
        
        // GC içeriğine göre renk kodlaması
        if (gcValue < 40) {
            indicator.classList.add('bg-warning');
            indicator.title = 'Düşük GC içeriği';
        } else if (gcValue > 60) {
            indicator.classList.add('bg-danger');
            indicator.title = 'Yüksek GC içeriği';
        } else {
            indicator.classList.add('bg-success');
            indicator.title = 'Optimal GC içeriği';
        }
    });
}

/**
 * Tarih ve saat için helper
 */
function formatDate(date) {
    const options = { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    };
    return new Date(date).toLocaleDateString('tr-TR', options);
}

/**
 * Süre formatlamak için helper
 */
function formatTime(seconds) {
    if (seconds === 'indefinite') {
        return 'Süresiz';
    }
    
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    
    if (minutes > 0) {
        return `${minutes} dk ${remainingSeconds} sn`;
    } else {
        return `${remainingSeconds} sn`;
    }
} 