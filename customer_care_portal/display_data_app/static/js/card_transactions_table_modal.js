// ON SELECTING ROW
$(".btn").on('click', function () {
    var a = $(this).parents("tr").find(".wallet").text();
    var c = $(this).parents("tr").find(".create_date").text();
    var d = $(this).parents("tr").find(".response_crete_date").text();
    var e = $(this).parents("tr").find(".amount").text();
    var f = $(this).parents("tr").find(".status").text();
    var g = $(this).parents("tr").find(".response").text();
    var p = "";
    if ( g.trim() === 'None'){
        //g = '{"responses":[' +  '{"resp":"None","log":"None" }]}';
        g = "No response";
    } else{
        g = JSON.stringify(JSON.parse(g), null, 2);
    }

    // CREATING DATA TO SHOW ON MODEL
    p += "<p id='a' name='wallet'>Wallet: " + a + " </p>";
    p +="<p id='c' name='create_date'>Create Date: " + c + "</p>";
    p +="<p id='d' name='response_create_date' >Response Create Date: "+ d + " </p>";
    p +="<p id='e' name='amount'>Amount: "+ e + " </p>";
    p +="<p id='f' name='status'>Status: "+ f + " </p>";
    p +="<p id='g' name='response'>Response: "+ g + " </p>";

    //CLEARING THE PREFILLED DATA
    $("#show-modal-data").empty();
    //WRITING THE DATA ON MODEL
    $("#show-modal-data").append(p);
});


