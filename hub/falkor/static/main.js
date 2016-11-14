var websocketProtocol;
if (window.location.protocol == 'https:') {
	websocketProtocol = 'wss';
} else {
	websocketProtocol = 'ws';
}


var socket = new FancyWebSocket(websocketProtocol+"://" + window.location.host + "/");

var template = document.getElementById('template').innerHTML;
var compiled_template = Handlebars.compile(template);

var workspace_details_template = document.getElementById('workspace_details').innerHTML;
var workspace_details = Handlebars.compile(workspace_details_template);

function update_search_terms() {
	$('.live-search-list .collection-item').each(function(){
		$(this).attr('data-search-term', $(this).find('.title').text().toLowerCase());
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
  console.log('select', data);
  data.info_str = JSON.stringify(data.info, null, 2);
  var rendered = workspace_details({workspace: data, request: request});
  $("#workspace-detail").empty().append(rendered);
  console.log($('.modal').modal());
  
  var rendered_listitem = compiled_template({workspace_: data});
  $('[data-workspace="'+data.id+'"]').replaceWith(rendered_listitem);
  update_search_terms();
  $('[data-workspace="'+data.id+'"]').addClass('active').siblings().removeClass('active');
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

socket.bind('notifications', function(data){
	console.log('notifications', data);
	var $toastContent = $('<span>'+data.message+'</span>');
  Materialize.toast($toastContent, 5000);
});


$(document).ready(function () {
	/*
	socket.bind('workspaces', function(){
		$('[data-workspace="'+31+'"]').click();
	});
	*/
	$('#workspaces').off().on('click', '.collection-item', function(e) {
		e.preventDefault();
		var $this = $(this);

		if ($this.hasClass('list-group-item')) {
			$this
				.addClass('active')
				.siblings()
					.removeClass('active');
		}
		socket.send('workspaces.select', {workspace_id: $this.attr('data-workspace')} );
		
		$('#workspace-list').animate({"width": '0%'}, 200).hide();
		$('#workspace-detail').css({'max-height': 'inherit'});
		$('.refresh').attr('data-workspace-selected', $this.attr('data-workspace'));
		$('.workspaceName').text($this.find('.title').text());
		$('.show-on-detail').removeClass('hide');
		$('.hide-on-detail').addClass('hide');
		
		$("#workspace-detail").empty().append('<div class="progress"><div class="indeterminate"></div></div>');
		return false;
	});
	
	$('.exit').click(function (e) {
		e.preventDefault();
		$('#workspace-list').animate({"width": '50%'}, 200).show();
		$('#workspace-detail').css({"max-height": '0px'});
		$('.refresh').attr('data-workspace-selected', null);
		$('.workspaceName').text('');
		$('.show-on-detail').addClass('hide');
		$('.hide-on-detail').removeClass('hide');
	});
	
	$('.refresh').click(function (e) {
		e.preventDefault();
		var workspace_id = $('.refresh').attr('data-workspace-selected');
		if (workspace_id) {
			socket.send('workspaces.select', {workspace_id: workspace_id} );
		}
	});
	
	$('#workspace-detail').off().on('click', '.workspace-controls button', function(e) {
		socket.send('workspaces.control', {workspace_id: $(this).parent().attr('data-workspace-id'), command: $(this).attr('data-command')} );
		$(this).addClass('disabled');
	});
	
	$("#add_workspace_button").click(function(e) {
     	e.preventDefault();
     	var data = {};
      $("form.add_workspace").serializeArray().map(function(x){data[x.name] = x.value;}); 
      
      if (data['editorType'] == undefined) {
      	console.log('validation error');
      	return true;
      }
      
     	socket.send('workspaces.add', data);
     	$("#editModal").modal('close');
     	return false;
    })
    
  $(document).on('click', "#add_share_button", function(e) {
     	e.preventDefault();
     	var data = {};
      $("form.add_share").serializeArray().map(function(x){data[x.name] = x.value;}); 
      
     	socket.send('workspaces.shares.add', data);
     	$("#shareAdd").modal('close');
     	return false;
    });
    
    $(document).on('click', "#remove_share_button", function(e) {
     	e.preventDefault();
     	var data = {};
     	data.username = $('[href=#shareRemove]').parents('[data-username]').attr('data-username');
     	
      $("form.remove_share").serializeArray().map(function(x){data[x.name] = x.value;}); 
      
     	socket.send('workspaces.shares.add', data);
     	$("#shareRemove").modal('close');
     	return false;
    });
	
	$('.live-search-box').on('keyup', function(){
		var searchTerm = $(this).val().toLowerCase();
	    $('.live-search-list .collection-item').each(function(){
	        if ($(this).filter('[data-search-term *= ' + searchTerm + ']').length > 0 || searchTerm.length < 1) {
	            $(this).show();
	        } else {
	            $(this).hide();
	        }
	    });
	});
			
});











$.fn.autocompleteWS = function (options) {
      // Defaults
      var defaults = {
        data: {
      "Apple": null,
      "Microsoft": null,
      "Google": 'http://placehold.it/250x250'
    }
      };

      options = $.extend(defaults, options);

      return this.each(function() {
        var $input = $(this);
        var data = options.data,
            $inputDiv = $input.closest('.input-field'); // Div to append on

        // Check if data isn't empty
        if (!$.isEmptyObject(data)) {
          // Create autocomplete element
          var $autocomplete = $('<ul class="autocomplete-content dropdown-content"></ul>');

          // Append autocomplete element
          if ($inputDiv.length) {
            $inputDiv.append($autocomplete); // Set ul in body
          } else {
            $input.after($autocomplete);
          }

          var highlight = function(string, $el) {
            var img = $el.find('img');
            var matchStart = $el.text().toLowerCase().indexOf("" + string.toLowerCase() + ""),
                matchEnd = matchStart + string.length - 1,
                beforeMatch = $el.text().slice(0, matchStart),
                matchText = $el.text().slice(matchStart, matchEnd + 1),
                afterMatch = $el.text().slice(matchEnd + 1);
            $el.html("<span>" + beforeMatch + "<span class='highlight'>" + matchText + "</span>" + afterMatch + "</span>");
            if (img.length) {
              $el.prepend(img);
            }
          };
          
          socket.bind('users.autocomplete', function(data){
						console.log('users.autocomplete', data);
						$autocomplete.empty();
						var users = data.users;
						for (var i in users) {
							var autocompleteOption = $('<li></li>');
							autocompleteOption.append('<img src="https://github.com/'+users[i].username+'.png?size=42" class="right circle"><span>'+ users[i].username +'</span>');
							$autocomplete.append(autocompleteOption);
	            highlight(data.query, autocompleteOption);
						}
					});

          // Perform search
          $input.on('keyup', function (e) {
            // Capture Enter
            if (e.which === 13) {
              $autocomplete.find('li').first().click();
              return;
            }

            var val = $input.val().toLowerCase();

            // Check if the input isn't empty
            if (val !== '') {
            	socket.send('users.autocomplete', {'username': val});
            }
          });

          // Set input value
          $autocomplete.on('click', 'li', function () {
            $input.val($(this).text().trim());
            $input.trigger('change');
            $autocomplete.empty();
          });
        }
      });
};