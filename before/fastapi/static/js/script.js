/**
 * AI Poster Generator Frontend
 * Handles poster generation UI and API interactions
 */

class PosterGenerator {
    constructor() {
        // DOM Elements
        this.elements = {
            dropZone: document.getElementById('dropZone'),
            fileInput: document.getElementById('fileInput'),
            browseBtn: document.getElementById('browseBtn'),
            previewContainer: document.getElementById('previewContainer'),
            logoPreview: document.getElementById('logoPreview'),
            removeLogoBtn: document.getElementById('removeLogoBtn'),
            generateBtn: document.getElementById('generateBtn'),
            promptTextarea: document.getElementById('prompt'),
            positionButtons: document.querySelectorAll('.position-btn'),
            initialPlaceholder: document.getElementById('initialPlaceholder'),
            loadingIndicator: document.getElementById('loadingIndicator'),
            resultContainer: document.getElementById('resultContainer'),
            generatedPoster: document.getElementById('generatedPoster'),
            enhancedPromptText: document.getElementById('enhancedPromptText'),
            downloadBtn: document.getElementById('downloadBtn')
        };

        // State
        this.state = {
            selectedPosition: 'bottom-right',
            logoFile: null,
            currentPosterUrl: null
        };

        // Initialize
        this.initEventListeners();
    }

    initEventListeners() {
        // Position buttons
        this.elements.positionButtons.forEach(button => {
            button.addEventListener('click', () => this.handlePositionSelect(button));
        });

        // Drag and drop handlers
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.highlightDropZone, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.unhighlightDropZone, false);
        });

        this.elements.dropZone.addEventListener('drop', (e) => this.handleDrop(e));
        this.elements.browseBtn.addEventListener('click', () => this.elements.fileInput.click());
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.elements.removeLogoBtn.addEventListener('click', () => this.removeLogo());
        this.elements.generateBtn.addEventListener('click', () => this.generatePoster());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadPoster());
    }

    // Event handlers
    handlePositionSelect(button) {
        this.elements.positionButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        this.state.selectedPosition = button.dataset.position;
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlightDropZone() {
        this.elements.dropZone.classList.add('highlight');
    }

    unhighlightDropZone() {
        this.elements.dropZone.classList.remove('highlight');
    }

    handleDrop(e) {
        const files = e.dataTransfer.files;
        this.handleFiles(files);
    }

    handleFileSelect(e) {
        this.handleFiles(e.target.files);
    }

    handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                this.state.logoFile = file;
                this.previewImage(file);
            } else {
                this.showAlert('Please select an image file.');
            }
        }
    }

    previewImage(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            this.elements.logoPreview.src = e.target.result;
            this.elements.previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    removeLogo() {
        this.state.logoFile = null;
        this.elements.previewContainer.style.display = 'none';
        this.elements.fileInput.value = '';
    }

    async generatePoster() {
        const prompt = this.elements.promptTextarea.value.trim();

        if (!prompt) {
            this.showAlert('Please enter a prompt for your poster.');
            return;
        }

        // Update UI state
        this.setLoadingState(true);

        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            formData.append('logo_position', this.state.selectedPosition);

            if (this.state.logoFile) {
                formData.append('logo', this.state.logoFile);
            }

            // Call FastAPI endpoint
            const response = await fetch('/api/generate', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.success) {
                this.displayResults(data.poster_url, data.enhanced_prompt);
                this.state.currentPosterUrl = data.poster_url;
            } else {
                throw new Error(data.error || 'Poster generation failed');
            }
        } catch (error) {
            console.error('Poster generation error:', error);
            this.showAlert(`Error: ${error.message}`);
            this.resetToInitialState();
        } finally {
            this.setLoadingState(false);
        }
    }

    downloadPoster() {
        if (!this.state.currentPosterUrl || this.state.currentPosterUrl.endsWith('#')) return;

        const link = document.createElement('a');
        link.href = this.state.currentPosterUrl;
        link.download = `poster-${Date.now()}.png`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    // UI Helpers
    setLoadingState(isLoading) {
        this.elements.initialPlaceholder.style.display = isLoading ? 'none' : 'flex';
        this.elements.resultContainer.style.display = 'none';
        this.elements.loadingIndicator.style.display = isLoading ? 'flex' : 'none';
    }

    displayResults(posterUrl, enhancedPrompt) {
        this.elements.generatedPoster.src = posterUrl;
        this.elements.enhancedPromptText.textContent = enhancedPrompt || "No enhanced prompt available";
        this.elements.resultContainer.style.display = 'block';
    }

    resetToInitialState() {
        this.elements.initialPlaceholder.style.display = 'flex';
        this.elements.resultContainer.style.display = 'none';
    }

    showAlert(message) {
        alert(message);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new PosterGenerator();
});
class ImageManager {
    constructor() {
        this.imageList = document.getElementById('image-list');
        this.uploadForm = document.getElementById('upload-form');
        this.fileInput = document.getElementById('file-input');
        this.initEventListeners();
        this.loadImages();
    }

    initEventListeners() {
        this.uploadForm.addEventListener('submit', (e) => this.handleUpload(e));
    }

    async loadImages() {
        try {
            const response = await fetch('/images/');
            const images = await response.json();

            this.imageList.innerHTML = '';
            images.forEach(img => {
                const imgElement = document.createElement('div');
                imgElement.className = 'image-item';
                imgElement.innerHTML = `
            <h3>${img.name}</h3>
            <img src="/images/${img.id}" alt="${img.name}">
          `;
                this.imageList.appendChild(imgElement);
            });
        } catch (error) {
            console.error('Error loading images:', error);
        }
    }

    async handleUpload(e) {
        e.preventDefault();

        if (!this.fileInput.files.length) {
            alert('Please select an image file');
            return;
        }

        const formData = new FormData();
        formData.append('file', this.fileInput.files[0]);

        try {
            const response = await fetch('/images/', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                this.loadImages(); // Refresh the image list
                this.fileInput.value = ''; // Clear the file input
            } else {
                throw new Error('Upload failed');
            }
        } catch (error) {
            console.error('Upload error:', error);
            alert('Failed to upload image');
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ImageManager();
});
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('prompt')) {
        new PosterGenerator();
    }
    
    if (document.getElementById('upload-form')) {
        new ImageManager();
    }
});
