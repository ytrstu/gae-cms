YUI().use("node-menunav", function(Y) {

	Y.all('.nav-dropdown').each(function(i) {

	    Y.on('contentready', function () {

	        this.plug(Y.Plugin.NodeMenuNav, { autoSubmenuDisplay: false, mouseOutHideDelay: 0 });

	    }, "#" + i.get('id'));

	});

});