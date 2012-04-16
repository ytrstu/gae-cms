YUI().use("node-menunav", function(Y) {

	Y.all('.content-permissions').each(function(i) {

	    Y.on("contentready", function () {

	        this.plug(Y.Plugin.NodeMenuNav, { autoSubmenuDisplay: false, mouseOutHideDelay: 0 });

	    }, "#" + i.get('id'));

	});

});