planseats = [].slice.call(document.querySelectorAll('.row__seat'))
placesDict = {}

var buttonBuy = document.querySelector(".action--buy");
var price_el = document.querySelector('.plan__price');
var price_value = price_el.dataset.price;

var sum_price = 0;

// select a seat on the seat plan
function initEvents() {
    // select a seat
    var onSeatSelect = function(ev) { selectSeat(ev.target); };
    planseats.forEach(function(planseat) {
        planseat.addEventListener('click', onSeatSelect);
    });

}


function selectSeat(planseat) {
    if( classie.has(planseat, 'row__seat--reserved') ) {
        return false;
    }
    console.log('selectSeat');
    // add/remove selected class
    classie.toggle(planseat, 'row__seat--selected');
    if (!document.querySelector('.row__seat--selected')){
        buttonBuy.setAttribute('disabled', true);
    }else{
        buttonBuy.removeAttribute('disabled');
    }
    var placesArr = Array.from(document.querySelectorAll('.row__seat--selected'));
    let count_sel_places = placesArr.length
    sum_price = price_value * count_sel_places;
    console.log(sum_price);
    let sum_price_div = document.getElementsByClassName("plan__sum__price");
    sum_price_div[0].innerHTML = "Вы выбрали " + placesArr.length + " билет(ов) на сумму " + sum_price + " руб.";
}


buttonBuy.onclick = function(){
    var placesArr = Array.from(document.querySelectorAll('.row__seat--selected'));
    let selectedPlaces = []
    placesArr.forEach(function(place, i, placesArr){
        // console.log(place.id);
        selectedPlaces.push(place.id);
        let el = document.createElement("input");
        el.type = 'hidden';
        el.name = 'ticket[]';
        el.value = place.id;
        let form = document.getElementById("buy-form");
        form.appendChild(el);
    });
    console.log(selectedPlaces);
}

initEvents();