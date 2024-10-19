document.getElementById("update-button").addEventListener("click",function(){
    const country =document.getElementById("country-list"). value
    const state =document.getElementById("state-list"). value
    localStorage.setItem("country",country)
    localStorage.setItem("state",state)
})
console.log(localStorage.getItem("country"))
console.log(localStorage.getItem("state"))
