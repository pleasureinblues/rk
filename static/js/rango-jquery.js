$(document).ready( function() {

    $(".dcm").click( function(event) {
        alert("You clicked me basterd!");
    });

    $(".abc").hover( function() {
            $(this).css('color', 'red');
    },
    function() {
            $(this).css('color', 'blue');
    });



});
