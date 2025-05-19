document.addEventListener('DOMContentLoaded', () => {
    new PosterGenerator();
});

class PosterGenerator {
    constructor() {
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
            downloadBtn: document.getElementById('downloadBtn'),
            promptError: document.getElementById('promptError')
        };

        this.state = {
            selectedPosition: 'bottom-right',
            logoFile: null,
            currentPosterUrl: null
        };

        this.initEventListeners();
    }

    initEventListeners() {
        this.elements.positionButtons.forEach(button => {
            button.addEventListener('click', () => this.handlePositionSelect(button));
        });

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.highlightDropZone.bind(this), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.elements.dropZone.addEventListener(eventName, this.unhighlightDropZone.bind(this), false);
        });

        this.elements.dropZone.addEventListener('drop', (e) => this.handleDrop(e));
        this.elements.browseBtn.addEventListener('click', () => this.elements.fileInput.click());
        this.elements.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        this.elements.removeLogoBtn.addEventListener('click', () => this.removeLogo());
        this.elements.generateBtn.addEventListener('click', () => this.generatePoster());
        this.elements.downloadBtn.addEventListener('click', () => this.downloadPoster());

        this.elements.promptTextarea.addEventListener('input', () => {
            const text = this.elements.promptTextarea.value.trim();
            this.elements.generateBtn.disabled = text.length === 0;
            if (text.length > 0) {
                this.elements.promptError.style.display = 'none';
            }
        });
    }

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
            this.elements.promptError.style.display = 'block';
            return;
        }

        this.setLoadingState(true);

        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            formData.append('logo_position', this.state.selectedPosition);
            if (this.state.logoFile) {
                formData.append('logo', this.state.logoFile);
            }

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
            this.showAlert('Failed to generate poster. Please try again later.');
            this.clearResults();
        } finally {
            this.setLoadingState(false);
        }
    }

    displayResults(posterUrl, enhancedPrompt) {
        this.elements.generatedPoster.src = posterUrl;
        this.elements.enhancedPromptText.textContent = enhancedPrompt;
        this.elements.resultContainer.style.display = 'block';
        this.elements.initialPlaceholder.style.display = 'none';
    }

    clearResults() {
        this.elements.generatedPoster.src = '#';
        this.elements.enhancedPromptText.textContent = '';
        this.elements.resultContainer.style.display = 'none';
        this.elements.initialPlaceholder.style.display = 'flex';
        this.state.currentPosterUrl = null;
    }

    setLoadingState(isLoading) {
        this.elements.loadingIndicator.style.display = isLoading ? 'flex' : 'none';
        this.elements.generateBtn.disabled = isLoading;
    }

    downloadPoster() {
        if (!this.state.currentPosterUrl) {
            this.showAlert('No poster available to download.');
            return;
        }

        const link = document.createElement('a');
        link.href = this.state.currentPosterUrl;
        link.download = 'poster.png';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    showAlert(message) {
        alert(message);
    }
}
