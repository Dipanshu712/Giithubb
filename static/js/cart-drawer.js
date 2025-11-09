document.addEventListener('DOMContentLoaded', () => {
  const cartData = [];

  const cartDrawer = document.getElementById('cartDrawer');
  const closeCartBtn = document.getElementById('close-cart-btn');
  const pageOverlay = document.getElementById('page-overlay');
  const cartItemsList = document.getElementById('cart-items');
  const cartAmount = document.querySelector('.js-cart-items-count');
  const cartSubtotal = document.getElementById('cart-subtotal');

  function openCartDrawer() {
    cartDrawer.classList.add('active');
    pageOverlay.classList.add('visible');
    document.body.classList.add('overflow-hidden');
    renderCartItems();
  }

  function closeCart() {
    cartDrawer.classList.remove('active');
    pageOverlay.classList.remove('visible');
    document.body.classList.remove('overflow-hidden');
  }

  closeCartBtn.addEventListener('click', closeCart);
  pageOverlay.addEventListener('click', closeCart);

  function renderCartItems() {
    cartItemsList.innerHTML = '';
    let totalQuantity = 0;
    let subtotal = 0;

    cartData.forEach((item, idx) => {
      totalQuantity += item.quantity;
      subtotal += parseFloat(item.price) * item.quantity;
      const li = document.createElement('li');
      li.className = "cart-drawer-item d-flex position-relative";
      li.innerHTML = `
        <div>
          <img loading="lazy" class="cart-drawer-item__img" src="${item.image}" alt="${item.title}">
        </div>
        <div class="cart-drawer-item__info flex-grow-1">
          <h6 class="cart-drawer-item__title fw-normal">${item.title}</h6>
          <p class="cart-drawer-item__option text-secondary">Color: ${item.color}</p>
          <p class="cart-drawer-item__option text-secondary">Size: ${item.size}</p>
          <div class="d-flex align-items-center justify-content-between mt-1">
            <div class="qty-control position-relative">
              <button class="qty-control__reduce" data-idx="${idx}">-</button>
              <input type="number" name="quantity" value="${item.quantity}" min="1" class="qty-control__number border-0 text-center" data-idx="${idx}">
              <button class="qty-control__increase" data-idx="${idx}">+</button>
            </div>
            <span class="cart-drawer-item__price money price">₹${(item.price * item.quantity).toFixed(2)}</span>
          </div>
        </div>
        <button class="btn-close-xs position-absolute top-0 end-0 js-cart-item-remove" data-idx="${idx}">&times;</button>
      `;
      cartItemsList.appendChild(li);
    });

    cartAmount.textContent = totalQuantity;
    cartSubtotal.textContent = `₹${subtotal.toFixed(2)}`;

    attachEventListeners();
  }

  function attachEventListeners() {
    // Increase quantity
    cartItemsList.querySelectorAll('.qty-control__increase').forEach(btn => {
      btn.onclick = function () {
        const idx = this.getAttribute('data-idx');
        cartData[idx].quantity++;
        renderCartItems();
      };
    });

    // Decrease quantity
    cartItemsList.querySelectorAll('.qty-control__reduce').forEach(btn => {
      btn.onclick = function () {
        const idx = this.getAttribute('data-idx');
        if (cartData[idx].quantity > 1) {
          cartData[idx].quantity--;
          renderCartItems();
        }
      };
    });

    // Quantity input change
    cartItemsList.querySelectorAll('.qty-control__number').forEach(input => {
      input.onchange = function () {
        const idx = this.getAttribute('data-idx');
        let val = parseInt(this.value);
        if (isNaN(val) || val < 1) val = 1;
        cartData[idx].quantity = val;
        renderCartItems();
      };
    });

    // Remove item
    cartItemsList.querySelectorAll('.js-cart-item-remove').forEach(btn => {
      btn.onclick = function () {
        const idx = this.getAttribute('data-idx');
        cartData.splice(idx, 1);
        renderCartItems();
      };
    });
  }

  // CSRF helper function for Django POST
  function getCSRFToken() {
    const cookie = document.cookie.split('; ').find(row => row.startsWith('csrftoken='));
    return cookie ? cookie.split('=')[1] : '';
  }

  // Attach add to cart buttons event
  document.querySelectorAll('.btn-addtocart.js-open-aside').forEach(btn => {
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      const prodId = this.getAttribute('data-product-id');
      fetch('/add_to_cart/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': getCSRFToken()
        },
        body: `product_id=${prodId}`
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          const newItem = {
            title: data.name,
            price: parseFloat(data.price),
            color: this.getAttribute('data-color') || 'Default',
            size: this.getAttribute('data-size') || 'M',
            image: data.img,
            quantity: 1
          };
          addItemToCart(newItem);
        } else {
          alert('Failed to add item to cart');
        }
      }).catch(() => alert('Error adding item to cart.'));
    });
  });

  function addItemToCart(item) {
    const existingIndex = cartData.findIndex(i =>
      i.title === item.title && i.color === item.color && i.size === item.size);

    if (existingIndex !== -1) {
      cartData[existingIndex].quantity += item.quantity;
    } else {
      cartData.push(item);
    }
    openCartDrawer();
  }
});
