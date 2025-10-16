async function loadLayout() {
  const headerHTML = await fetch("components/header.html").then(r => r.text());
  const footerHTML = await fetch("components/footer.html").then(r => r.text());
  document.getElementById("header").innerHTML = headerHTML;
  document.getElementById("footer").innerHTML = footerHTML;
}
loadLayout();
