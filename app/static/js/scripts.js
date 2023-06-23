// Get all the anchor elements inside the left pane
const leftPaneLinks = document.querySelectorAll('.left-pane a');

// Attach a click event listener to each anchor element
leftPaneLinks.forEach((link) => {
  link.addEventListener('click', (event) => {
    event.preventDefault(); // Prevent the default link behavior

    const targetId = link.getAttribute('href'); // Get the target section's ID

    // Hide all sections in the main section
    const sections = document.querySelectorAll('.main-section .section');
    sections.forEach((section) => {
      section.style.display = 'none';
    });

    // Show the selected section in the main section
    const targetSection = document.querySelector(targetId);
    targetSection.style.display = 'block';
  });
});

