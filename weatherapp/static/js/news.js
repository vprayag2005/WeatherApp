function news_display(news_url,newstype) {
    fetch(news_url) // Adjust the URL to match your URL pattern
    .then(response => {
        if (response.ok) {
            return response.json(); // Parse JSON if the response is OK
        }
        throw new Error('Network response was not ok.');
    })
    .then(data => {
        console.log(data);// Process the JSON data
        if(newstype=="cardtype_news"){
            const cardContainer = document.querySelector('.row.row-cols-1.row-cols-md-3.g-4');
            for (let index = 0; index < data.images_link.length; index++) {
                const card =document.createElement('div')
                card.className=('col')
                card.innerHTML = `
                    <a href="${data.news_link[index].news_link}">
                        <div class="card h-100">
                        <img src=" ${data.images_link[index].img_link}" class="card-img-top" alt="...">
                        <div class="card-body">
                            <h5 class="card-title">${data.headlines[index].headline}</h5>
                        </div>
                        <div class="card-footer">
                            <small class="text-muted">Last updated 3 mins ago</small>
                        </div>
                        </div>
                    </a>
                `;
                cardContainer.append(card)
            }
            
        }
        else{
            const newslist =document.querySelector(".list-group")
            for (let index = 0; index < data.headlines.length; index++) {
                const list=document.createElement('div')
                list.className=('list')
                list.innerHTML=`
                  <a href="${data.news_links[index].news_link}" class="list-group-item list-group-item-action " aria-current="true">
                    <div class="d-flex w-100 justify-content-between">
                    <h5 class="mb-1">${data.headlines[index].headline}</h5>
                    <small>${data.pubDates[index].pubDate}</small>
                    </div>
                    <small>${data.Sources[index].source}</small>
                </a>
                <br>
                `
                newslist.append(list)
                
            }
        }
    })
    .catch(error => console.error('Error fetching data:', error));

    
};
const get_id=document.querySelector("h1")
if (get_id.id == "global"){
    news_display("/news/newsglobal/","cardtype_news");
}else if (get_id.id == "national"){
    news_display("/news/newsnational/","cardtype_news");
}else if(localStorage.getItem("state")== "Kerala"){
    news_display("/news/newskerala/","cardtype_news");
}else if(localStorage.getItem("state")=="Karnataka"){
    news_display("/news/newskarnataka/","listtype_news");
}
