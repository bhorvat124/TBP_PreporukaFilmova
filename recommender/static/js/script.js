window.onload = getAllMovies;
var allMovies;
var recommendedMovies = [];
var preferredMovies = [];

function getAllMovies(){
    $('#showRecommendedMoviesBtn').hide();
    $.ajax({
        type: "GET",
        url: "/get_all_movies",
        dataType: "json",
        success: function(data){
            allMovies = data;
            for (let i = 0; i < allMovies.length; i++) {
                var averageRating = allMovies[i].ratings.rating.reduce((a, b) => a + b) / allMovies[i].ratings.rating.length;
                allMovies[i].averageRating = Number(averageRating).toFixed(2);
                allMovies[i].totalRatings = allMovies[i].ratings.rating.length;
            }
            showTableWithAllMovies();
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            alert("Status: " + textStatus); alert("Error: " + errorThrown); 
        } 
    });

    getPreferredMovies();
}

function showTableWithAllMovies(){
    $('#showRecommendedMoviesBtn').hide();
    $("#moviesTable").DataTable().clear();
    $("#moviesTable").DataTable().destroy();

    for (let i = 0; i < allMovies.length; i++) {
        

        var button;
        if(preferredMovies.includes(allMovies[i]._id)){
            button = '<input type="button" id="'+allMovies[i]._id+'" value="Remove preference" style="width:100%; cursor: pointer;"'
            + 'onclick="preferMovie(\''+ allMovies[i]._id +'\')">';
        }
        else{
            button = '<input type="button" id="'+allMovies[i]._id+'" value="Prefer" style="width:100%; cursor: pointer;"'
            + 'onclick="preferMovie(\''+ allMovies[i]._id +'\')">';
        }
        var row = "<tr>"+
                "<td>" + allMovies[i].title + "</td>" +
                "<td>" + allMovies[i].genres.join(", ") + "</td>" +
                "<td>" + allMovies[i].averageRating + "</td>" +
                "<td>" + allMovies[i].totalRatings + "</td>" +
                '<td align="center">'+ button + '</td></tr>';

        $("#moviesTable").append(row);
    }
    
    $("#moviesTable").DataTable();
}

function getRecommendedMovies(){
    $.ajax({
        type: "POST",
        url: "/get_recommended_movies",
        contentType: 'application/json',
        data: JSON.stringify({'data': preferredMovies}),
        success: function(data){
            recommendedMovies = data;
            for (let i = 0; i < recommendedMovies.length; i++) {
                var averageRating = recommendedMovies[i].ratings.rating.reduce((a, b) => a + b) / recommendedMovies[i].ratings.rating.length;
                recommendedMovies[i].averageRating = Number(averageRating).toFixed(2);
                recommendedMovies[i].totalRatings = recommendedMovies[i].ratings.rating.length;
            }
            showRecommendedMovies(true);
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            alert("Status: " + textStatus); alert("Error: " + errorThrown); 
        } 
    });
}

function showRecommendedMovies(refreshTable){
    if(refreshTable){
        $("#moviesTable").DataTable().clear();
        $("#moviesTable").DataTable().destroy();
    }
    for (let i = 0; i < recommendedMovies.length; i++) {
        var row = "<tr>"+
                "<td>" + recommendedMovies[i].title + "</td>" +
                "<td>" + recommendedMovies[i].genres.join(", ") + "</td>" +
                "<td>" + recommendedMovies[i].averageRating + "</td>" +
                "<td>" + recommendedMovies[i].totalRatings + "</td>" +
                '<td align="center"></td></tr>';

        $("#moviesTable").append(row);
        
    }
    $("#moviesTable").DataTable();
}

function recommendedMoviesClicked(){
    $("#moviesTable").DataTable().clear();
    $("#moviesTable").DataTable().destroy();
    $('#showRecommendedMoviesBtn').show();
    if(recommendedMovies != null && recommendedMovies.length > 0){
        showRecommendedMovies(false);
    }
}

function preferMovie(movieId){
    movieId = Number(movieId);
    if($('#' + movieId).attr('value') == "Prefer"){
        $.ajax({
            type: "POST",
            url: "/set_preferred_movie",
            contentType: 'application/json',
            data: JSON.stringify({'data': movieId}),
            success: function(data){
                preferredMovies.push(movieId);
                $('#' + movieId).val("Remove preference");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            } 
        });
    }
    else{
        $.ajax({
            type: "POST",
            url: "/remove_preferred_movie",
            contentType: 'application/json',
            data: JSON.stringify({'data': movieId}),
            success: function(data){
                const index = preferredMovies.indexOf(movieId);
                if (index > -1) {
                    preferredMovies.splice(index, 1);
                }
                $('#' + movieId).val("Prefer");
            },
            error: function(XMLHttpRequest, textStatus, errorThrown) { 
                alert("Status: " + textStatus); alert("Error: " + errorThrown); 
            } 
        });
    }
}

function getPreferredMovies(){
    $.ajax({
        type: "POST",
        url: "/get_preferred_movies",
        contentType: 'application/json',
        data: JSON.stringify({'data': ''}),
        success: function(data){
            preferredMovies = data;
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            alert("Status: " + textStatus); alert("Error: " + errorThrown); 
        } 
    });
}