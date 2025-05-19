document.addEventListener('DOMContentLoaded', function() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const previewContainer = document.getElementById('previewContainer');
    const logoPreview = document.getElementById('logoPreview');
    const removeLogoBtn = document.getElementById('removeLogoBtn');
    const generateBtn = document.getElementById('generateBtn');
    const promptTextarea = document.getElementById('prompt');
    const positionButtons = document.querySelectorAll('.position-btn');
    const initialPlaceholder = document.getElementById('initialPlaceholder');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const resultContainer = document.getElementById('resultContainer');
    const generatedPoster = document.getElementById('generatedPoster');
    const enhancedPromptText = document.getElementById('enhancedPromptText');
    const downloadBtn = document.getElementById('downloadBtn');

    let selectedPosition = 'bottom-right';
    let logoFile = null;

    // Handle logo position selection
    positionButtons.forEach(button => {
        button.addEventListener('click', function() {
            positionButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            selectedPosition = this.dataset.position;
        });
    });

    // Handle drag and drop for logo
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('highlight');
    }

    function unhighlight() {
        dropZone.classList.remove('highlight');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    browseBtn.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFileSelect);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }

    function handleFileSelect(e) {
        handleFiles(e.target.files);
    }

    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('image/')) {
                logoFile = file;
                previewImage(file);
            } else {
                alert('Please select an image file.');
            }
        }
    }

    function previewImage(file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            logoPreview.src = e.target.result;
            previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }

    removeLogoBtn.addEventListener('click', function() {
        logoFile = null;
        previewContainer.style.display = 'none';
        fileInput.value = '';
    });

    // Handle poster generation
    generateBtn.addEventListener('click', generatePoster);

    async function generatePoster() {
        const prompt = promptTextarea.value.trim();

        if (!prompt) {
            alert('Please enter a prompt for your poster.');
            return;
        }

        // Show loading state
        initialPlaceholder.style.display = 'none';
        resultContainer.style.display = 'none';
        loadingIndicator.style.display = 'flex';

        try {
            const formData = new FormData();
            formData.append('prompt', prompt);
            formData.append('logo_position', selectedPosition);

            if (logoFile) {
                formData.append('logo', logoFile);
            }

            const response = await fetch('/generate', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                // Show result
                generatedPoster.src = data.poster_url;
                enhancedPromptText.textContent = data.enhanced_prompt || "No enhanced prompt generated.";

                loadingIndicator.style.display = 'none';
                resultContainer.style.display = 'block';
            } else {
                throw new Error(data.error || 'Failed to generate poster');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('An error occurred while generating the poster: ' + error.message);

            loadingIndicator.style.display = 'none';
            initialPlaceholder.style.display = 'flex';
        }
    }

    // Handle poster download
    downloadBtn.addEventListener('click', function() {
        if (generatedPoster.src && !generatedPoster.src.endsWith('#')) {
            const link = document.createElement('a');
            link.href = generatedPoster.src;
            link.download = 'poster-' + new Date().getTime() + '.png';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        }
    });
});