let console_div = document.querySelector('.console')
let state_div = document.querySelector('.state')

async function addPin() {
    let pinid = document.getElementById('pinid').value
    let pinmode = document.getElementById('pinmode').value
    let resp = await fetch('/api/pin/add/' + pinid + '/' + pinmode)
    let data = await resp.json()
    console.log(data)
    if (data.status == 'ok') {
        let pindiv = document.createElement('div')
        pindiv.classList.add('pin')
        pindiv.innerText = pinid
        pindiv.addEventListener('click', function () {
            fetch('/api/pin/toggle/' + pinid)
        })

        state_div.append(pindiv)
    } else {
        M.toast({ html: 'Pin not added' })
    }
}

function loadPin() {
    // loop through the pins and display the dataset of each pin
    var pins = document.querySelectorAll('.pin')
    pins.forEach(pin => {
        pin.addEventListener('click', function () {
            fetch('/api/pin/toggle/' + pin.dataset.pinId)
        })
        pin.innerText = pin.dataset.pinId
    })
}


async function getServerFeedback() {
    // fetch /api/log/latest
    // display the response in the console

    resp = await fetch('/api/log/full/latest')
    data = await resp.json()
    console_div.innerText = data
    // scroll to bottom if the user is not scrolling up
    if (console_div.scrollTop >= (console_div.scrollHeight - console_div.offsetHeight - 1000)) {
        console.log(console_div.scrollTop - (console_div.scrollHeight - console_div.offsetHeight - 100))
        console_div.scrollTop = console_div.scrollHeight
    }

}
console.scrollTop = console.scrollHeight
//setInterval(getServerFeedback, 1000)
loadPin()