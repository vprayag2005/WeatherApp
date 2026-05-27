const searchbox = document.querySelector(".search input")
const searchbtn = document.querySelector(".search button")
const weatherIcon = document.querySelector(".weather-icon")
const weatherStatus = document.querySelector(".weather-status")
const locationStatus = document.getElementById("location-status")
const useLocationButton = document.getElementById("use-location-button")
const degreeUnit = "\u00B0C"
const pageMode = window.weatherConfig?.mode || document.body.dataset.weatherMode || "search"
const savedHomeLabel = window.weatherConfig?.savedHomeLabel || ""
const savedHomeQuery = window.weatherConfig?.savedHomeQuery || ""

function getWeatherIcon(condition) {
	const map = {
		Clouds: staticCloudsUrl,
		Clear: staticClearUrl,
		Rain: staticRainUrl,
		Drizzle: staticDrizzleUrl,
		Mist: staticMistUrl,
		Snow: typeof staticSnowUrl !== "undefined" ? staticSnowUrl : "",
	}
	return map[condition] || ""
}

function formatWeatherLabel(value) {
	return value ? value.replace(/\b\w/g, char => char.toUpperCase()) : ""
}

function setText(selector, value) {
	const element = document.querySelector(selector)
	if (element) {
		element.innerHTML = value
	}
}

function setLocationStatus(message) {
	if (locationStatus) {
		locationStatus.textContent = message
	}
}

function getCookie(name) {
	if (!document.cookie) {
		return null
	}
	const match = document.cookie
		.split(";")
		.map(cookie => cookie.trim())
		.find(cookie => cookie.startsWith(name + "="))
	return match ? decodeURIComponent(match.split("=")[1]) : null
}

async function fetchWeather(payload) {
	const formData = new FormData()
	Object.entries(payload).forEach(([key, value]) => {
		if (value !== undefined && value !== null && value !== "") {
			formData.append(key, value)
		}
	})

	const response = await fetch("/fetch-data/", {
		method: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		body: formData,
	})
	const weatherData = await response.json()

	if (!response.ok || weatherData.error) {
		throw new Error(weatherData.error || "Failed to fetch weather data")
	}

	return weatherData
}

function renderCurrentWeather(data) {
	const currentCondition = formatWeatherLabel(
		data.weather?.[0]?.description || data.weather?.[0]?.main || ""
	)
	const windSpeed = data.wind?.speed ? Math.round(data.wind.speed * 3.6) : 0

	setText(".city", data.name)
	setText(".temp", `${Math.round(data.main.temp)} ${degreeUnit}`)
	setText(".humdity", `${data.main.humidity} %`)
	setText(".wind", `${windSpeed} km/h`)
	setText(".pressure", `${data.main.pressure} hPa`)
	setText(".max-temp", `${Math.round(data.main.temp_max)} ${degreeUnit}`)
	setText(".min-temp", `${Math.round(data.main.temp_min)} ${degreeUnit}`)
	setText(".feel-temp", `${Math.round(data.main.feels_like)} ${degreeUnit}`)

	if (weatherStatus) {
		weatherStatus.innerHTML = currentCondition
	}

	if (weatherIcon) {
		weatherIcon.src = getWeatherIcon(data.weather?.[0]?.main)
		weatherIcon.alt = currentCondition ? `${currentCondition} icon` : "Current weather icon"
	}
}

function renderHourlyForecast(hourlyData) {
	for (let i = 0; i < 8; i++) {
		const entry = hourlyData.list[i]
		if (!entry) {
			continue
		}

		const slideIcon = document.querySelector(`#silde${i} .silde-img`)
		setText(`#silde${i} .silde-time`, entry.dt_txt.split(" ")[1])
		if (slideIcon) {
			slideIcon.src = getWeatherIcon(entry.weather?.[0]?.main)
			slideIcon.alt = formatWeatherLabel(entry.weather?.[0]?.main || "")
		}
		setText(`#silde${i} .silde-temp`, `${Math.round(entry.main.temp)} ${degreeUnit}`)
		setText(`#silde${i} .silde-rainfall`, entry.rain ? `${entry.rain["3h"]} mm` : "")
	}
}

function renderFiveDayForecast(hourlyData) {
	setText(".left-content #day0", "Tomorrow")
	const daysOfWeek = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
	const now = new Date()
	let dayIndex = now.getDay() + 2
	let hourlyIndex = 0

	for (let index = 0; index < 5; index++) {
		if (dayIndex > 6) {
			dayIndex = 0
		}
		if (document.querySelector(`.left-content #day${index + 1}`)) {
			setText(`.left-content #day${index + 1}`, daysOfWeek[dayIndex])
			dayIndex += 1
		}

		const forecastDate = new Date(now)
		forecastDate.setDate(now.getDate() + index + 1)
		const formattedDate = forecastDate.toISOString().split("T")[0]

		const weatherCounts = {}
		let minDayTemp = 0
		let maxDayTemp = 0
		let count = 0
		let maxCount = 0
		let common = ""
		let foundDate = false

		for (; hourlyIndex < hourlyData.list.length; hourlyIndex++) {
			const currentEntry = hourlyData.list[hourlyIndex]
			if (currentEntry.dt_txt.split(" ")[0] === formattedDate) {
				foundDate = true
				const value = currentEntry.weather?.[0]?.main || ""
				minDayTemp += currentEntry.main.temp_min
				maxDayTemp += currentEntry.main.temp_max
				count += 1
				weatherCounts[value] = (weatherCounts[value] || 0) + 1
				if (weatherCounts[value] > maxCount) {
					maxCount = weatherCounts[value]
					common = value
				}
			} else if (foundDate) {
				break
			}
		}

		setText(`.left-content #status${index}`, formatWeatherLabel(common))
		const forecastIcon = document.querySelector(`#imgday${index}`)
		if (forecastIcon) {
			forecastIcon.src = getWeatherIcon(common)
			forecastIcon.alt = common ? `${formatWeatherLabel(common)} icon` : ""
		}

		if (count > 0) {
			setText(`#max_temp${index}`, `${Math.round(maxDayTemp / count)} ${degreeUnit}`)
			setText(`#min_temp${index}`, `${Math.round(minDayTemp / count)} ${degreeUnit}`)
		} else {
			setText(`#max_temp${index}`, `-- ${degreeUnit}`)
			setText(`#min_temp${index}`, `-- ${degreeUnit}`)
		}
	}
}

async function weathercheck(payload, options = {}) {
	try {
		const weatherData = await fetchWeather(payload)
		const currentWeather = weatherData[0]
		const forecastData = weatherData[1]

		renderCurrentWeather(currentWeather)
		renderHourlyForecast(forecastData)
		renderFiveDayForecast(forecastData)

		const defaultSuccessMessage =
			pageMode === "home"
				? "Showing live weather for your current location."
				: `Showing weather for ${currentWeather.name}.`

		setLocationStatus(options.successMessage || defaultSuccessMessage)
	} catch (error) {
		console.error("Error:", error)
		setLocationStatus(error.message)
		if (pageMode !== "home") {
			console.error(`Error: ${error.message}`)
		}
	}
}

function searchWeather() {
	if (!searchbox) {
		return
	}
	const city = searchbox.value.trim()
	if (!city) {
		return
	}
	setLocationStatus(`Searching weather for ${city}...`)
	weathercheck({ city })
	searchbox.value = ""
}

function loadSavedHomeWeather(reasonMessage) {
	if (!savedHomeQuery) {
		return false
	}

	setLocationStatus(reasonMessage || `Loading saved home weather for ${savedHomeLabel}...`)
	weathercheck(
		{ city: savedHomeQuery },
		{ successMessage: `Showing saved home weather for ${savedHomeLabel}.` }
	)
	return true
}

function loadCurrentLocationWeather() {
	if (!navigator.geolocation) {
		if (!loadSavedHomeWeather("Location access is not available in this browser. Loading saved home weather instead...")) {
			setLocationStatus(
				"Location access is not available in this browser. Use Find Weather to search manually."
			)
		}
		return
	}

	setLocationStatus("Getting your current location...")
	navigator.geolocation.getCurrentPosition(
		position => {
			weathercheck({
				lat: position.coords.latitude,
				lon: position.coords.longitude,
			})
		},
		() => {
			if (!loadSavedHomeWeather("Location access was blocked. Loading saved home weather instead...")) {
				setLocationStatus(
					"Location access was blocked. Use Find Weather to search another city manually."
				)
			}
		},
		{
			enableHighAccuracy: true,
			timeout: 10000,
			maximumAge: 300000,
		}
	)
}

if (searchbtn && searchbox) {
	searchbtn.addEventListener("click", searchWeather)
	searchbox.addEventListener("keydown", event => {
		if (event.key === "Enter") {
			event.preventDefault()
			searchWeather()
		}
	})
}

if (useLocationButton) {
	useLocationButton.addEventListener("click", loadCurrentLocationWeather)
}

if (pageMode === "home") {
	loadCurrentLocationWeather()
} else {
	setLocationStatus("Search for any city to load weather details.")
}
