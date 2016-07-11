window.onload = function() {
	console.log("RUNNING AMIP")
	function resizeWrapper(){	
		var wrapper = document.getElementById("wrapper")
		var topOffset = window.innerHeight/20;
		var top = (window.innerHeight/2)-(wrapper.clientHeight/2)-topOffset;
		wrapper.style.marginTop = top+"px";
	}
	resizeWrapper();
	window.addEventListener("resize", resizeWrapper);
}
