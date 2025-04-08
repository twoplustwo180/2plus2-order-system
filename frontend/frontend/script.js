const menu = [
  { name: '香煎鮮魚', price: 580 },
  { name: '豚香檸檬鹽麴', price: 450 },
  { name: '苦茶油雞', price: 480 },
  { name: '匈牙利燉牛肉', price: 480 },
  { name: '嫩煎雞腿咖哩飯', price: 300 },
  { name: '蔬食咖哩飯', price: 300 },
  { name: '綜合炸物拼盤', price: 280 },
  { name: '香柚茶', price: 150 },
  { name: '可可牛奶', price: 150 },
];

const cart = JSON.parse(localStorage.getItem('cart') || '[]');
const menuContainer = document.getElementById('menu');

if (menuContainer) {
  menu.forEach(item => {
    const div = document.createElement('div');
    div.className = 'border p-4 rounded shadow';
    div.innerHTML = `<div class="text-lg font-bold mb-2">${item.name}</div>
                     <div class="mb-2">$${item.price}</div>
                     <button class="bg-blue-600 text-white px-4 py-2 rounded" onclick='addToCart("${item.name}", ${item.price})'>加入購物車</button>`;
    menuContainer.appendChild(div);
  });
}

function addToCart(name, price) {
  cart.push({ name, price });
  localStorage.setItem('cart', JSON.stringify(cart));
  alert(`${name} 已加入購物車！`);
}
