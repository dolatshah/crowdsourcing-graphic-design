// JavaScript Document
$(document).ready(function(e) {
	
	//centering full size image modal
	$(".inner").hover(function(){
		$(this).css({'box-shadow' : '0 0 10px blue'})
	}, function(){
		$(this).css({'box-shadow' : ''})
		});
	
	
	$(".comment").hover(function(){
		$(this).find(".latent").css({'visibility' : 'visible'})
		}, function(){
			$(this).find(".latent").css({'visibility' : ''})
		});
	$(".comment > .latent").click(function(){
		if($(this).hasClass("show")){
			$(this).parent().animate({height:"20px"}, function(){
			$(this).find(".show").addClass("latent");
			$(this).find(".show").removeClass("show");
			$(this).find(".latent").css({'visibility' : 'hidden'});
		});
			}
		else{
			$(".show").parent().animate({height:"20px"}, function(){
			$(this).find(".show").addClass("latent");
			$(this).find(".show").removeClass("show");
			$(this).find(".latent").css({'visibility' : 'hidden'});
		});
			
			$(this).parent().animate({height:$(".commentChild").height() + 20}, function(){
			$(this).find(".latent").addClass("show");
			$(this).find(".latent").removeClass("latent");
			});
		};		
	});
	


		

//show zoom designed image

		function isMouseOn($tools){
			$tools.mouseleave(function(){
				$tools.animate({left:'5px'}, 500);
			});
			return;
		}
		
		$(".image").on("mouseenter", function(){
			$(this).find('.hover').stop(true, true).fadeIn();
			$(this).find('.hover').find('img').stop().animate
			({width:'60px', height:'60px', top:'90px', left:'90px'}, 500);
			$tools = $(this).parent().find(".tools");
    		$tools.stop(true, true).animate({left:'55px'}, 500);
			if($tools.mouseenter() == 0){
				$tools.stop();
				};
		});
		
    	$(".image").on("mouseleave", function(){
        	$(this).find('.hover').stop(true, true).fadeOut();
			$(this).find('.hover').find('img').animate
			({width:'30px', height:'30px', top:'105px', left:'105px'}, 100);
			$tools = $(this).parent().find(".tools");
			$tools.stop(true, true).animate({left:'5px'}, 500);
			$tools.mouseover(function(){
				$tools.stop().animate({left:'55px'}, 500);
				isMouseOn($tools);
				});
    	});

});
