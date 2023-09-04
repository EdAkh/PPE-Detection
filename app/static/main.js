// main.js

document.addEventListener("DOMContentLoaded", function () {
    // Get references to elements
    const contentContainer = document.getElementById("content-container");
    const detectForm = document.getElementById("detect-form");
    const detectedImageContainer = document.getElementById("detected-image-container");

    // Function to toggle the text color and display the success message
    function showSuccessMessage() {
        var uploadStatus = document.getElementById("upload-status");
        var successMessage = document.getElementById("success-message");

        // Change the text color to green
        uploadStatus.style.color = "green";

        // Display the success message
        successMessage.style.display = "block";
    }

    // Example: You can call this function when the upload is successful
    // Replace this with the actual logic of your upload process
    var uploadSuccessful = true;  // Set this based on your logic

    if (uploadSuccessful) {
        showSuccessMessage();
    }

    // Attach an event listener to the detection form
    detectForm.addEventListener("submit", function (event) {
        event.preventDefault();

        // Use AJAX to submit the form data to the /detect_object route
        fetch("/detect_object", {
            method: "GET", // Use GET or POST as appropriate for your route
            headers: {
                "Content-Type": "application/json",
            },
        })
        .then((response) => response.text()) // Convert the response to text
        .then((data) => {
            // Update the content container with the response data
            contentContainer.innerHTML = data;

            // Example: You can call toggleTextColor when the upload is successful
            // Replace this with the actual logic of your upload process
            var uploadSuccessful = true;  // Set this based on your logic
            toggleTextColor(uploadSuccessful);

            // Call updateAnnotatedImage to display the detected image in detectedImageContainer
            updateAnnotatedImage();
        })
        .catch((error) => {
            console.error("Error:", error);
        });
    });

});
