// Register service worker for PWA
if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("sw.js")
    .then(reg => console.log("Service Worker registered:", reg))
    .catch(err => console.error("SW registration failed:", err));
}
