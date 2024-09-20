fetch('/news/newsglobal/') // Adjust the URL to match your URL pattern
    .then(response => {
        if (response.ok) {
            return response.json(); // Parse JSON if the response is OK
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log(data); // Process the JSON data
    })
    .catch(error => console.error('Error fetching data:', error));
