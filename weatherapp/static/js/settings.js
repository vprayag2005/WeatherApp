const autofillButton = document.getElementById("autofill-location-button")
const settingsLocationStatus = document.getElementById("settings-location-status")
const cityInput = document.getElementById("settings-city")
const stateInput = document.getElementById("settings-state")
const countryInput = document.getElementById("settings-country")
const settingsConfig = window.settingsConfig || {}

function setSettingsStatus(message) {
	if (settingsLocationStatus) {
		settingsLocationStatus.textContent = message
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

async function resolveLocation(position) {
	const formData = new FormData()
	formData.append("lat", position.coords.latitude)
	formData.append("lon", position.coords.longitude)

	const response = await fetch(settingsConfig.resolveLocationUrl, {
		method: "POST",
		headers: { "X-CSRFToken": getCookie("csrftoken") },
		body: formData,
	})
	const payload = await response.json()

	if (!response.ok || payload.error) {
		throw new Error(payload.error || "We could not resolve your location.")
	}

	return payload
}

function fillLocationFields(location) {
	if (countryInput && location.country) {
		if (![...countryInput.options].some(o => o.value === location.country)) {
			countryInput.add(new Option(location.country, location.country));
		}
		countryInput.value = location.country;
		
		fetchStates(location.country).then(() => {
			if (stateInput && location.state) {
				if (![...stateInput.options].some(o => o.value === location.state)) {
					stateInput.add(new Option(location.state, location.state));
				}
				stateInput.value = location.state;
				
				if (cityInput && location.city) {
					cityInput.value = location.city;
				}
			}
		});
	}
}

function requestLocationAutofill() {
	if (!navigator.geolocation) {
		setSettingsStatus("Location access is not available in this browser. Please enter your home location manually.")
		return
	}

	setSettingsStatus("Requesting browser location to fill your city, state, and country...")
	navigator.geolocation.getCurrentPosition(
		async position => {
			try {
				setSettingsStatus("Finding your city details...")
				const location = await resolveLocation(position)
				fillLocationFields(location)
				setSettingsStatus(`Filled your location as ${location.label}. Review it and save when ready.`)
			} catch (error) {
				setSettingsStatus(error.message)
			}
		},
		() => {
			setSettingsStatus("Location access was blocked. Please enter your city, state, and country manually.")
		},
		{
			enableHighAccuracy: true,
			timeout: 10000,
			maximumAge: 300000,
		}
	)
}

if (autofillButton) {
	autofillButton.addEventListener("click", requestLocationAutofill)
}

if (settingsConfig.shouldAutoLocate) {
	requestLocationAutofill()
}

function populateSelect(selectElement, options, selectedValue) {
	if (!selectElement) return;
	
	while (selectElement.options.length > 1) {
		selectElement.remove(1);
	}
	
	let found = false;
	for (const opt of options) {
		const option = document.createElement("option");
		option.value = opt;
		option.text = opt;
		if (opt === selectedValue) {
			option.selected = true;
			found = true;
		}
		selectElement.add(option);
	}
	
	if (selectedValue && !found) {
		const option = document.createElement("option");
		option.value = selectedValue;
		option.text = selectedValue;
		option.selected = true;
		selectElement.add(option);
	}
}

async function fetchCountries() {
	try {
		const response = await fetch("https://countriesnow.space/api/v0.1/countries/iso");
		const payload = await response.json();
		if (payload && !payload.error) {
			const countries = payload.data.map(c => c.name);
			populateSelect(countryInput, countries, countryInput.value);
		}
	} catch (e) {
		console.error("Failed to fetch countries", e);
	}
}

async function fetchStates(country) {
	if (!country) {
		populateSelect(stateInput, [], stateInput.value);
		return;
	}
	try {
		const response = await fetch("https://countriesnow.space/api/v0.1/countries/states", {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify({ country: country })
		});
		const payload = await response.json();
		if (payload && !payload.error) {
			const states = payload.data.states.map(s => s.name);
			populateSelect(stateInput, states, stateInput.value);
		}
	} catch (e) {
		console.error("Failed to fetch states", e);
	}
}

// fetchCities removed because city is now a text input

if (countryInput) {
	countryInput.addEventListener("change", (e) => {
		fetchStates(e.target.value);
	});
}

async function initializeDropdowns() {
	await fetchCountries();
	if (countryInput && countryInput.value) {
		await fetchStates(countryInput.value);
	}
}

initializeDropdowns();
