$(document).ready(function() {
  $('.display').each(function() {
    var table = $(this).DataTable({
      searching: true, // Disable global search
      ordering: false,
      paging: true, // Enable pagination
      autoWidth: true // Disable automatic column width adjustment
    });

    // Add individual column search functionality
    $('tfoot th', this).each( function () {
      var title = $(this).text();
      $(this).html( '<input type="text" placeholder="Search '+title+'" />' );
    });

    // Apply the search
    table.columns().every( function () {
      var that = this;

      $( 'input', this.footer() ).on( 'keyup change clear', function () {
        if ( that.search() !== this.value ) {
          that
            .search( this.value )
            .draw();
        }
      });
    });
  });
});

