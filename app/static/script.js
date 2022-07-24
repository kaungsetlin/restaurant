m.route.prefix = "";

function addtoCart(id) {
  qty = document.getElementById(`qty-${id}`).value
  console.log('insert into cart session', id);
  m.route.set('/addtocart/:id/:qty', {id: id, qty: qty});
};

function removefromCart(id) {
  m.route.set('/remove/:id', {id: id});
};
