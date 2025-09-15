/**
 * Maps Module - handles Leaflet map functionality for barbershop locations
 */

class MapsManager {
    constructor() {
        this.map = null;
        this.markers = [];
        this.config = {
            defaultCenter: [30.0444, 31.2357], // Cairo coordinates
            defaultZoom: 13,
            tileLayer: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            attribution: '© OpenStreetMap contributors'
        };
        this.init();
    }

    init() {
        this.initializeMap();
        this.bindEvents();
    }

    initializeMap() {
        const mapContainer = document.getElementById('map');
        if (!mapContainer || typeof L === 'undefined') return;

        try {
            // Initialize map
            this.map = L.map('map').setView(this.config.defaultCenter, this.config.defaultZoom);

            // Add tile layer
            L.tileLayer(this.config.tileLayer, {
                attribution: this.config.attribution,
                maxZoom: 18
            }).addTo(this.map);

            // Load existing location if available
            this.loadExistingLocation();

            // Setup location picker if in edit mode
            if (mapContainer.dataset.editable === 'true') {
                this.setupLocationPicker();
            }

            // Load barbershop markers if in list view
            this.loadBarbershopMarkers();

        } catch (error) {
            console.error('Map initialization failed:', error);
            this.showMapError('فشل في تحميل الخريطة');
        }
    }

    loadExistingLocation() {
        const latInput = document.getElementById('id_latitude');
        const lngInput = document.getElementById('id_longitude');
        
        if (latInput?.value && lngInput?.value) {
            const lat = parseFloat(latInput.value);
            const lng = parseFloat(lngInput.value);
            
            if (!isNaN(lat) && !isNaN(lng)) {
                this.map.setView([lat, lng], 15);
                this.addMarker(lat, lng, 'موقع الصالون');
            }
        }
    }

    setupLocationPicker() {
        // Add click handler for location selection
        this.map.on('click', (e) => {
            this.selectLocation(e.latlng.lat, e.latlng.lng);
        });

        // Add current location button
        this.addCurrentLocationButton();

        // Add search functionality
        this.addLocationSearch();
    }

    selectLocation(lat, lng) {
        // Clear existing markers
        this.clearMarkers();

        // Add new marker
        this.addMarker(lat, lng, 'الموقع المحدد');

        // Update form inputs
        console.log('=== MAPS.JS SELECT LOCATION DEBUG ===');
        console.log('Received coordinates:', { lat, lng });
        
        const latInput = document.getElementById('id_latitude');
        const lngInput = document.getElementById('id_longitude');
        
        console.log('Found latitude input:', !!latInput, latInput);
        console.log('Found longitude input:', !!lngInput, lngInput);
        
        if (latInput) {
            const latValue = lat.toFixed(6);
            latInput.value = latValue;
            console.log('Set latitude value:', latValue, 'Current value:', latInput.value);
        } else {
            console.error('Latitude input field not found!');
        }
        
        if (lngInput) {
            const lngValue = lng.toFixed(6);
            lngInput.value = lngValue;
            console.log('Set longitude value:', lngValue, 'Current value:', lngInput.value);
        } else {
            console.error('Longitude input field not found!');
        }
        
        // Double check the values after setting
        console.log('Final check - Lat field value:', latInput ? latInput.value : 'NOT FOUND');
        console.log('Final check - Lng field value:', lngInput ? lngInput.value : 'NOT FOUND');

        // Show success message
        window.NotificationManager?.success('تم تحديد الموقع بنجاح');

        // Trigger custom event
        this.triggerEvent('locationSelected', { lat, lng });
    }

    addCurrentLocationButton() {
        const button = L.control({ position: 'topright' });
        
        button.onAdd = () => {
            const div = L.DomUtil.create('div', 'leaflet-bar leaflet-control leaflet-control-custom');
            div.innerHTML = '<button type="button" title="موقعي الحالي"><i class="fas fa-crosshairs"></i></button>';
            div.style.backgroundColor = 'white';
            div.style.width = '40px';
            div.style.height = '40px';
            div.style.cursor = 'pointer';
            
            div.onclick = () => this.getCurrentLocation();
            
            return div;
        };
        
        button.addTo(this.map);
    }

    getCurrentLocation() {
        if (!navigator.geolocation) {
            window.NotificationManager?.error('المتصفح لا يدعم تحديد الموقع');
            return;
        }

        const button = document.querySelector('.leaflet-control-custom button');
        const originalContent = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        navigator.geolocation.getCurrentPosition(
            (position) => {
                const { latitude, longitude } = position.coords;
                this.map.setView([latitude, longitude], 15);
                this.selectLocation(latitude, longitude);
                button.innerHTML = originalContent;
            },
            (error) => {
                console.error('Geolocation error:', error);
                window.NotificationManager?.error('فشل في تحديد موقعك الحالي');
                button.innerHTML = originalContent;
            },
            {
                enableHighAccuracy: true,
                timeout: 10000,
                maximumAge: 60000
            }
        );
    }

    addLocationSearch() {
        const searchContainer = document.createElement('div');
        searchContainer.className = 'map-search-container mb-3';
        searchContainer.innerHTML = `
            <div class="input-group">
                <input type="text" class="form-control" placeholder="ابحث عن موقع..." id="location-search">
                <button class="btn btn-outline-secondary" type="button" id="search-btn">
                    <i class="fas fa-search"></i>
                </button>
            </div>
        `;

        const mapContainer = document.getElementById('map');
        mapContainer.parentNode.insertBefore(searchContainer, mapContainer);

        // Bind search events
        const searchInput = document.getElementById('location-search');
        const searchBtn = document.getElementById('search-btn');

        searchBtn.addEventListener('click', () => this.searchLocation(searchInput.value));
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                this.searchLocation(searchInput.value);
            }
        });
    }

    async searchLocation(query) {
        if (!query.trim()) return;

        const searchBtn = document.getElementById('search-btn');
        const originalContent = searchBtn.innerHTML;
        searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            // Using Nominatim API for geocoding
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&countrycodes=eg`
            );
            
            const results = await response.json();
            
            if (results.length > 0) {
                const result = results[0];
                const lat = parseFloat(result.lat);
                const lng = parseFloat(result.lon);
                
                this.map.setView([lat, lng], 15);
                this.selectLocation(lat, lng);
                
                window.NotificationManager?.success(`تم العثور على: ${result.display_name}`);
            } else {
                window.NotificationManager?.warning('لم يتم العثور على نتائج للبحث');
            }

        } catch (error) {
            console.error('Search error:', error);
            window.NotificationManager?.error('فشل في البحث عن الموقع');
        } finally {
            searchBtn.innerHTML = originalContent;
        }
    }

    loadBarbershopMarkers() {
        const markersData = window.barbershopMarkers;
        if (!markersData || !Array.isArray(markersData)) return;

        markersData.forEach(barbershop => {
            if (barbershop.latitude && barbershop.longitude) {
                const marker = this.addMarker(
                    barbershop.latitude,
                    barbershop.longitude,
                    barbershop.name,
                    this.createPopupContent(barbershop)
                );

                // Store barbershop data with marker
                marker.barbershopData = barbershop;
            }
        });

        // Fit map to show all markers
        if (this.markers.length > 0) {
            const group = new L.featureGroup(this.markers);
            this.map.fitBounds(group.getBounds().pad(0.1));
        }
    }

    addMarker(lat, lng, title, popupContent = null) {
        const marker = L.marker([lat, lng]).addTo(this.map);
        
        if (popupContent) {
            marker.bindPopup(popupContent);
        } else if (title) {
            marker.bindPopup(title);
        }

        this.markers.push(marker);
        return marker;
    }

    createPopupContent(barbershop) {
        return `
            <div class="barbershop-popup">
                <h6 class="mb-2">${barbershop.name}</h6>
                <p class="mb-1 small text-muted">${barbershop.address || 'لا يوجد عنوان'}</p>
                ${barbershop.phone ? `<p class="mb-1 small"><i class="fas fa-phone"></i> ${barbershop.phone}</p>` : ''}
                <div class="mt-2">
                    <a href="/barbershops/${barbershop.id}/" class="btn btn-sm btn-primary">عرض التفاصيل</a>
                    <a href="/bookings/create/?barbershop=${barbershop.id}" class="btn btn-sm btn-success">احجز الآن</a>
                </div>
            </div>
        `;
    }

    clearMarkers() {
        this.markers.forEach(marker => {
            this.map.removeLayer(marker);
        });
        this.markers = [];
    }

    showMapError(message) {
        const mapContainer = document.getElementById('map');
        if (mapContainer) {
            mapContainer.innerHTML = `
                <div class="alert alert-warning text-center p-4">
                    <i class="fas fa-map-marked-alt fa-2x mb-3"></i>
                    <p class="mb-0">${message}</p>
                </div>
            `;
        }
    }

    bindEvents() {
        // Listen for window resize to invalidate map size
        window.addEventListener('resize', () => {
            if (this.map) {
                setTimeout(() => this.map.invalidateSize(), 100);
            }
        });

        // Listen for tab changes (if map is in a tab)
        document.addEventListener('shown.bs.tab', (e) => {
            if (this.map && e.target.getAttribute('href') === '#map-tab') {
                setTimeout(() => this.map.invalidateSize(), 100);
            }
        });
    }

    triggerEvent(eventName, data) {
        const event = new CustomEvent(`maps:${eventName}`, { detail: data });
        document.dispatchEvent(event);
    }

    // Public API methods
    setCenter(lat, lng, zoom = 15) {
        if (this.map) {
            this.map.setView([lat, lng], zoom);
        }
    }

    addBarbershop(barbershop) {
        if (barbershop.latitude && barbershop.longitude) {
            return this.addMarker(
                barbershop.latitude,
                barbershop.longitude,
                barbershop.name,
                this.createPopupContent(barbershop)
            );
        }
    }

    destroy() {
        if (this.map) {
            this.map.remove();
            this.map = null;
        }
        this.markers = [];
    }
}

// Auto-initialize when DOM is ready and Leaflet is available
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('map') && typeof L !== 'undefined') {
        window.MapsManager = new MapsManager();
    }
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MapsManager;
}
