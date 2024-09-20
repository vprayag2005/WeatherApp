const searchbox = document.querySelector(".search input")
const searchbtn = document.querySelector(".search button")
const weather_icon = document.querySelector(".weather-icon")
async function weathercheck(city) {
	const formData = new FormData();
	formData.append('city', city);
	try {
		const response = await fetch('/fetch-data/', {
			method: 'POST',
			headers: {
				'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is sent
			},
			body: formData
		});
		const weather_data = await response.json();
		const data =weather_data[0]
		const data_hourly =weather_data[1]
		console.log('Data received from Django:', data,data_hourly);
		document.querySelector(".city").innerHTML = data.name
		document.querySelector(".temp").innerHTML = Math.round(data.main.temp) + " °C"
		document.querySelector(".humdity").innerHTML = data.main.humidity + " %"
		document.querySelector(".wind").innerHTML = data.wind.speed + " km/h"
		document.querySelector(".pressure").innerHTML = data.main.pressure + " Pa"
		document.querySelector(".max-temp").innerHTML = Math.round(data.main.temp_max) + " °C"
		document.querySelector(".min-temp").innerHTML = Math.round(data.main.temp_min) + " °C"
		document.querySelector(".feel-temp").innerHTML = Math.round(data.main.feels_like) + " °C"
		if (data.weather[0].main == "Clouds") {
			weather_icon.src = staticCloudsUrl
		} else if (data.weather[0].main == "Clear") {
			weather_icon.src = staticClearUrl
		} else if (data.weather[0].main == "Rain") {
			weather_icon.src = staticRainUrl
		} else if (data.weather[0].main == "Drizzle.png") {
			weather_icon.src = staticDrizzleUrl
		} else if (data.weather[0].main == "Mist") {
			weather_icon.src = staticMistUrl
		}
		for (let index = 0; index < 8; index++) {
			document.querySelector(`#silde${index} .silde-time`).innerHTML = data_hourly.list[index].dt_txt.split(' ')[1]
			const hourly_icon = document.querySelector(`#silde${index} .silde-img`)
			if (data_hourly.list[index].weather[0].main == "Clouds") {
				hourly_icon.src = staticCloudsUrl
			} else if (data_hourly.list[index].weather[0].main == "Clear") {
				hourly_icon.src = staticClearUrl
			} else if (data_hourly.list[index].weather[0].main == "Rain") {
				hourly_icon.src = staticRainUrl
			} else if (data_hourly.list[index].weather[0].main == "Drizzle.png") {
				hourly_icon.src = staticDrizzleUrl
			} else if (data_hourly.list[index].weather[0].main == "Mist") {
				hourly_icon.src = staticMistUrl
			}
			document.querySelector(`#silde${index} .silde-temp`).innerHTML = Math.round(data_hourly.list[index].main.temp) + " °C"
			if (data_hourly.list[index].rain) {
				document.querySelector(`#silde${index} .silde-rainfall`).innerHTML = data_hourly.list[index].rain["3h"] + "mm"
			}
		}
		document.querySelector(".left-content #day0").innerHTML = "Tomorrow"
		let i = 0
		let flag = 1
		const now = new Date()
		let day_index = now.getDay() + 2
		for (let index = 0; index < 5; index++) {
			let dict = {}
			let min_day_temp=0
			let max_day_temp=0
			let count=0
			let max_count = 0
			let common = ""
			const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
			if (day_index > 6) {
				day_index = 0
			}
			if (document.querySelector(`.left-content #day${index + 1}`)) {
				document.querySelector(`.left-content #day${index + 1}`).innerHTML = (daysOfWeek[day_index])
				day_index++
			}
			const year = now.getFullYear();
			var month = String(now.getMonth() + 1).padStart(2, '0');
			var day = String(now.getDate()).padStart(2, '0');
			var formattedDate = `${year}-${month}-${String(parseInt(day, 10) + 1 + index).padStart(2, '0')}`
			console.log(formattedDate)
			for (i; i < 40; i++) {
				if (data_hourly.list[i].dt_txt.split(' ')[0] == formattedDate) {
					flag = 0
					var value = data_hourly.list[i].weather[0].main
					min_day_temp+=data_hourly.list[i].main.temp_min
					max_day_temp+=data_hourly.list[i].main.temp_max
					count++
					if (value in dict) {
						dict[value] += 1
					} else {
						dict[value] = 1
					}
					if (dict[value] > max_count) {
						max_count = dict[value]
						common = value
					}
				} else {
					if (flag == 0) {
						break
					}
				}
			}
			document.querySelector(`.left-content #status${index}`).innerHTML = common
			const day_icon = document.querySelector(`#imgday${index}`)
			if (common == "Clouds") {
				day_icon.src = staticCloudsUrl
			} else if (common == "Clear") {
				day_icon.src = staticClearUrl
			} else if (common == "Rain") {
				day_icon.src = staticRainUrl
			} else if (common == "Drizzle.png") {
				day_icon.src = staticDrizzleUrl
			} else if (common == "Mist") {
				day_icon.src = staticMistUrl
			}
			document.querySelector(`#max_temp${index}`).innerHTML = Math.round(max_day_temp/count)+" °C"
			document.querySelector(`#min_temp${index}`).innerHTML = Math.round(min_day_temp/count)+" °C"	
		}
	} catch (error) {
		console.error('Error:', error);
	}
}

searchbtn.addEventListener("click", () => {
	if (searchbox.value) {
		console.log(searchbox.value+"hshakfjwhfish")
		weathercheck(searchbox.value)
		searchbox.value=""
	}
})

var container = document.getElementById('container')
var slider = document.getElementById('slider');
var slides = document.getElementsByClassName('slide').length;
var buttons = document.getElementsByClassName('btn');

var currentPosition = 0;
var currentMargin = 0;
var slidesPerPage = 0;
var slidesCount = slides - slidesPerPage;
var containerWidth = container.offsetWidth;
var prevKeyActive = false;
var nextKeyActive = true;

window.addEventListener("resize", checkWidth);

function checkWidth() {
	containerWidth = container.offsetWidth;
	setParams(containerWidth);
}

function setParams(w) {
	console.log(w)
	if (w < 600) {
		slidesPerPage = 1;
	}else if(w<768){
		slidesPerPage = 2
	}else{
		slidesPerPage=5
	}
	slidesCount = slides - slidesPerPage;
	if (currentPosition > slidesCount) {
		currentPosition -= slidesPerPage;
	};
	currentMargin = - currentPosition * (100 / slidesPerPage);
	slider.style.marginLeft = currentMargin + '%';
	if (currentPosition > 0) {
		buttons[0].classList.remove('inactive');
	}
	if (currentPosition < slidesCount) {
		buttons[1].classList.remove('inactive');
	}
	if (currentPosition >= slidesCount) {
		buttons[1].classList.add('inactive');
	}
}

setParams();

function slideRight() {
	if (currentPosition != 0) {
		slider.style.marginLeft = currentMargin + (100 / slidesPerPage) + '%';
		currentMargin += (100 / slidesPerPage);
		currentPosition--;
	};
	if (currentPosition === 0) {
		buttons[0].classList.add('inactive');
	}
	if (currentPosition < slidesCount) {
		buttons[1].classList.remove('inactive');
	}
};

function slideLeft() {
	if (currentPosition != slidesCount) {
		slider.style.marginLeft = currentMargin - (100 / slidesPerPage) + '%';
		currentMargin -= (100 / slidesPerPage);
		currentPosition++;
	};
	if (currentPosition == slidesCount) {
		buttons[1].classList.add('inactive');
	}
	if (currentPosition > 0) {
		buttons[0].classList.remove('inactive');
	}
};
        // Function to get CSRF token from cookies
        function getCookie(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        }