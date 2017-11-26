var
  show_list_url = '',
  show_item_url = '', 
  update_item_url = '', 
  remove_item_url = '', 
  create_item_url = '', 
  current_name,

  init = function(show_url, item_url, update_url, remove_url, create_url) {
      show_list_url = show_url;
      show_item_url = item_url;
      update_item_url = update_url;
      remove_item_url = remove_url;
      create_item_url = create_url;
      $('#update').on('click', on_update);
      $('#delete').on('click', on_remove);
      $('#create').on('click', on_create);
      load();
  },

  load = function() {
    $.ajax({
      url: show_list_url
    })
    .done(show_list)
    .fail(show_error);
  },

  show_error = function() {
    alert('An error occurred');
  },

  on_name = function(ev) {
    current_name = $('#table_names').DataTable().row(this).data()[0];
    $.ajax({
        url: show_item_url + '/' + current_name
      })
      .done(show_content)
      .fail(show_error);
  },

  show_content = function(data) {
    $('#content').val(data)
  },

  on_update = function(ev) {
    if (current_name == undefined) {
        return;
    }
    $.post( update_item_url + '/' + current_name, {
      'content': $('#content').val()
    })
    .done(function() { $('#status').text('Item updated'); });
  },

  on_remove = function(ev) {
    if (confirm("Are you sure?")) {
      $.post(remove_item_url + '/' + current_name).done(function() { $('#status').text('Item removed'); load() });
    } else {
      // ok
    }
  },

  on_create = function(ev) {
    var title = prompt("Enter a title for the new item.");
    if (title != null) {
      $.post(create_item_url + '/' + title).done(function(response) { 
          if (response == 'created') {
              $('#status').text('Item added'); 
              load() 
          }
          else {
              $('#status').text('Item exists'); 
          }});
    }
  },

  show_list = function(data) {
    var converted = [];
    for (var i in data["data"]) {
        converted.push([data["data"][i]]);
    }
    $('#table_names').DataTable({
        "destroy": true,
        "paging": true,
        "iDisplayLength": 10,
        "searching": true,
        "bInfo" : false,
        "data": converted,
        "select": {
            style: 'os',
            selector: 'td:first-child'
        }
      });
      $('#table_names tbody').on('click', 'tr', on_name);
      $('.main').height(($('.sidebar').height()));
      $('#content').val('Select an item');
  }