// main.js

// Execute this code when the DOM (Document Object Model) is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Get references to HTML elements by their IDs
    const showImageButton = document.getElementById('show-image');
    const showAnnotatedImageButton = document.getElementById('show-annotated-image');
    const imageDisplay = document.getElementById('image-display');

    // Add a click event listener to the "Show Image" button
    showImageButton.addEventListener('click', () => {
        // Fetch the image from the '/display' route using a GET request
        fetch('/display', {
            method: 'GET',
        })
        .then(response => response.blob()) // Convert the response to a Blob
        .then(blob => {
            // Create a URL for the Blob and set it as the source of the image element
            const imageUrl = URL.createObjectURL(blob);
            imageDisplay.src = imageUrl;
            imageDisplay.style.display = 'block'; // Display the image element
        })
        .catch(error => {
            console.error('Error fetching image:', error);
        });
    });

    // Add a click event listener to the "Show Annotated Image" button
    showAnnotatedImageButton.addEventListener('click', () => {
        // Fetch the annotated image from the '/display_detection' route using a GET request
        fetch('/display_detection', {
            method: 'GET',
        })
        .then(response => response.blob()) // Convert the response to a Blob
        .then(blob => {
            // Create a URL for the Blob and set it as the source of the image element
            const imageUrl = URL.createObjectURL(blob);
            imageDisplay.src = imageUrl;
            imageDisplay.style.display = 'block'; // Display the image element
        })
        .catch(error => {
            console.error('Error fetching annotated image:', error);
        });
    });
});
