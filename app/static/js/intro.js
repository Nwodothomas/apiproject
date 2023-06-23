const introSection = document.getElementById('intro');
let offset = 0;

function animateBackground() {
  offset -= 1;
  introSection.style.backgroundPosition = `${offset}px 0`;
}

setInterval(animateBackground, 100); // Adjust the time interval (in milliseconds) as per your preference
