async function newsapi(){
    try {
        const response = await fetch('/news/sports_news/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken') // Ensure CSRF token is sent
            },
        });
        const data = await response.json();
        console.log(data)
        newscard=document.getElementById("newscard")
        for (let index = 0; index < data.articles.length; index++) {
            const englishPattern = /^[a-zA-Z0-9\s,.'\"!?;:()&-]+$/;
            if (data.articles[index].urlToImage  && englishPattern.test(data.articles[index].description) && englishPattern.test(data.articles[index].title) ) {
                const card =document.createElement("div")
                card.className=("col")
                card.innerHTML=
                `
                <a href=${data.articles[index].url}>
                    <div class="card h-100">
                        <img src=${data.articles[index].urlToImage} class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">${data.articles[index].title}</h5>
                            <p class="card-title"><strong>Source:-${data.articles[index].source.name}</strong></p>
                            <p class="card-text">${data.articles[index].description}</p>
                        </div>
                    </div>
                </a>`
                newscard.append(card)
            }
            
        }
    }
    catch (error) {
        console.error('Error:', error);
    }


}
newsapi();
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