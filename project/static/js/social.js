//fb
jQuery.ajax( { 
  url: '//freegeoip.net/json/', 
  type: 'POST', 
  dataType: 'jsonp',
  success: function(location) {
  loc = location.country_code.substr(0,2) 
  if(loc != "IR") {
  $("#fbshare").show();
  $(window).resize(function(){
       if ($(window).width() <= 768) {  
  $("#push,.footer").css("height","810px");
  $("#wrapper").css("margin-bottom","-810px");
       }     
  });
	  (function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0];
  if (d.getElementById(id)) return;
  js = d.createElement(s); js.id = id;
  js.src = "//connect.facebook.net/en_US/sdk.js#xfbml=1&version=v2.0";
  fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));
}
  }
} );
