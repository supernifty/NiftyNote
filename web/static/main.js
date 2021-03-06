var
  show_list_url = '',
  show_item_url = '', 
  update_item_url = '', 
  remove_item_url = '', 
  create_item_url = '', 
  rename_item_url = '', 
  loaded_content = '', 
  unsaved = false,
  current_name,

  init = function(show_url, item_url, update_url, remove_url, create_url, rename_url) {
      var renderer = new marked.Renderer();
      renderer.table = function(header, body) {
        return "<table class='table table-striped'><thead>" + 
            header + 
            "</thead><tbody>" + 
            body + 
            "</tbody></table>";
      }
      marked.setOptions({
        renderer: renderer
      });
      show_list_url = show_url;
      show_item_url = item_url;
      update_item_url = update_url;
      remove_item_url = remove_url;
      create_item_url = create_url;
      rename_item_url = rename_url;
      $('#update').on('click', on_save);
      $('#delete').on('click', on_remove);
      $('#create').on('click', on_create);
      $('#edit').on('click', on_edit);
      $('#cancel').on('click', on_cancel);
      $('#rename').on('click', on_rename);
      $("#content").on('change keyup paste mouseup', content_changed);
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

  content_changed = function() {
    if ($(this).val() != loaded_content) {
      unsaved = true;
    }
  },

  on_name = function(ev) {
    if (!unsaved || confirm("'" + current_name + "' has not been saved. Are you sure?")) {
      current_name = $('#table_names').DataTable().row(this).data()[0];
      $.ajax({
          url: show_item_url + '/' + current_name
        })
        .done(show_content)
        .fail(show_error);
    }
    else {
      return false;
    }
  },

  show_content = function(data) {
    loaded_content = data;
    unsaved = false;
    $('#title').text(current_name);
    $('#content').val(data);
    render(data);
    $('#update,#cancel,#content,#delete').hide();
    $('#edit,#rendered,#rename').show();
  },

  render = function(data) {
    $('#rendered').html(marked(data));
    MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
  },

  on_save = function(ev) {
    if (current_name == undefined) {
        return;
    }
    var content = $('#content').val(); 
    $.post( update_item_url + '/' + current_name, {
      'content': content
    })
    .done(function() { 
      $('#status').text('Saved "' + current_name + '"'); 
      loaded_content = content;
      unsaved = false;
      render(content);
      $('#edit,#rendered').show();
      $('#content,#update,#cancel,#delete').hide();
    });
  },

  on_remove = function(ev) {
    if (confirm("Are you sure you want to remove '" + current_name + "'?")) {
      $.post(remove_item_url + '/' + current_name).done(function() { 
        $('#status').text('Item removed'); 
        load() 
      });
    } else {
      // not removed
    }
  },

  on_rename = function(ev) {
    var title = prompt("Enter the new title.", current_name);
    if (title != null) {
      $.post(rename_item_url + '/' + current_name + '/' + title + '/').done(function(response) { 
          if (response == 'renamed') {
              $('#status').text('Item renamed.'); 
              current_name = title;
              $('#title').text(current_name);
          }
          else {
              $('#status').text('Proposed name already exists.'); 
          }});
    }
  },

  on_create = function(ev) {
    var title = prompt("Enter a title for the new item.");
    if (title != null) {
      $.post(create_item_url + '/' + title).done(function(response) { 
          if (response == 'created') {
              $('#status').text('Item added'); 
              load();
          }
          else {
              $('#status').text('Item exists'); 
          }});
    }
  },

  on_edit = function(ev) {
    $('#update,#cancel,#content,#delete').show();
    $('#edit,#rendered').hide();
    $('#status').text(''); 
  },

  on_cancel = function(ev) {
    $('#update,#cancel,#content,#delete').hide();
    $('#edit,#rendered').show();
  },


  show_list = function(data) {
    var converted = data["data"];
    $('#table_names').DataTable({
        "destroy": true,
        "paging": true,
        "iDisplayLength": 25,
        "searching": true,
        "bInfo" : false,
        "data": converted,
        "select": {
            style: 'os',
            selector: 'td:first-child'
        },
        "columnDefs": [
          {
            "targets": [1],
            "visible": false,
            "searchable": true
          }
        ]
      });
      $('#table_names tbody').on('click', 'tr', on_name);
      $('.main').height(($('.sidebar').height()));
      $('#rendered').val('Select an item');
      $('#update,#cancel,#content,#delete,#edit,#rename').hide();
  }
