var socket = new FancyWebSocket("ws://" + window.location.host + "/ws/");

var template = document.getElementById('template').innerHTML;
var compiled_template = Handlebars.compile(template);

var workspace_details_template = document.getElementById('workspace_details').innerHTML;
var workspace_details = Handlebars.compile(workspace_details_template);

function update_search_terms() {
	$('.live-search-list a').each(function(){
		$(this).attr('data-search-term', $(this).find('.list-group-item-heading').text().toLowerCase());
	});
}

socket.bind('workspaces.update_state', function(data){
  console.log(data);
  $('[data-workspace="'+data.workspace__pk+'"] .status').text(data.status);
});

socket.bind('workspaces.update', function(data){
  console.log(data);
  var rendered = compiled_template({workspace_: data});
  $('[data-workspace="'+data.id+'"]').replaceWith(rendered);
  update_search_terms();
});

socket.bind('workspaces.created', function(data){
  console.log(data);
  var rendered = compiled_template({workspace_: data});
  $("#workspaces").prepend(rendered);
  update_search_terms();
});

socket.bind('workspaces.deleted', function(data){
  console.log(data);
  $('[data-workspace="'+data.id+'"]').remove();
});

socket.bind('workspaces.select', function(data){
  console.log(data);
  data.info = JSON.stringify(data.info, null, 2);
  var rendered = workspace_details({workspace: data, request: request});
  $("#workspace-detail").empty().append(rendered);
});

socket.bind('workspaces', function(data){
	$("#workspaces").empty();
	for (workspace in data.workspaces) {
		workspace = data.workspaces[workspace]
		var rendered = compiled_template({workspace_: workspace});
		$("#workspaces").append(rendered);
	}
	update_search_terms();
});

$(document).ready(function () {
	$('#workspaces').off().on('click', 'a.pjax', function(e) {
		e.preventDefault();
		var $this = $(this);

		if ($this.hasClass('list-group-item')) {
			$this
				.addClass('active')
				.siblings()
					.removeClass('active');
		}
		socket.send('workspaces.select', {workspace_id: $this.attr('data-workspace')} );
		
		return false;
	});
	
	$("#add_workspace_button").click(function(e) {
     	e.preventDefault();
     	var data = {};
        $("form.add_workspace").serializeArray().map(function(x){data[x.name] = x.value;}); 
     	socket.send('workspaces.add', data);
     	$("#editModal").modal('hide');
     	return false;
    });
	
	$('.live-search-box').on('keyup', function(){
		var searchTerm = $(this).val().toLowerCase();
	    $('.live-search-list a').each(function(){
	        if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
	            $(this).show();
	        } else {
	            $(this).hide();
	        }
	    });
	});
			
});