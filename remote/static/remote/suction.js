const slider = document.getElementById('suction-level');
const levels = JSON.parse(document.getElementById('suction-levels').textContent);
const labels = {gentle: 'Suave', normal: 'Normal', strong: 'Fuerte', eco: 'Eco', max: 'Máxima'};
function updateSuctionLabel() {
  const value = levels[Number(slider.value)];
  const label = labels[value] || value;
  document.getElementById('suction-label').textContent = label;
  slider.setAttribute('aria-valuetext', label);
}
slider.addEventListener('input', updateSuctionLabel);
updateSuctionLabel();
