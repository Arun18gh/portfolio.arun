let currentIndex = 0;
let images = [];

function openLightbox(index) {
  images = Array.from(document.querySelectorAll(".gallery-img")).map(img => img.src);
  currentIndex = index;
  document.getElementById("lightbox-img").src = images[currentIndex];
  document.getElementById("lightbox").style.display = "block";
}

function closeLightbox() {
  document.getElementById("lightbox").style.display = "none";
}

function nextImage() {
  currentIndex = (currentIndex + 1) % images.length;
  document.getElementById("lightbox-img").src = images[currentIndex];
}

function prevImage() {
  currentIndex = (currentIndex - 1 + images.length) % images.length;
  document.getElementById("lightbox-img").src = images[currentIndex];
}
// Fade-in on scroll
document.addEventListener("scroll", function() {
  const elements = document.querySelectorAll(".fade-in");
  elements.forEach(el => {
    const rect = el.getBoundingClientRect();
    if (rect.top < window.innerHeight - 100) {
      el.classList.add("visible");
    }
  });
});
