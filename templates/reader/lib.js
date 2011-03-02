Ext.ns('Reader');


Reader.SubscriptionPanel = Ext.extend(Ext.Panel, {
	constructor: function(application, config) {
		this.application = application;
		var self = this;
		
		var listView = this.listView = new Ext.list.ListView({
			emptyText: 'No Subscriptions',
			store: this.application.subscription_store,
			columns: [
				{
					header: 'Title',
					dataIndex: 'title',
					width: .75,
				},
				{
					header: 'Unread',
					dataIndex: 'unread',
					align: 'right',
				},
			],
			hideHeaders: true,
			singleSelect: true,
			loadingText: 'Loading...',
		});
		
		Reader.SubscriptionPanel.superclass.constructor.call(this, Ext.applyIf(config||{}, {
			title: 'Subscriptions',
			items: [
				this.listView,
			],
			bbar: [
				{
					text: 'Add Feed...',
					iconCls: 'icon-add-feed',
					handler: function() {
						Ext.MessageBox.prompt('Add Feed', 'Enter the URL to the feed:', function(button, text) {
							if (button == 'ok') {
								Ext.Ajax.request({
									url: '{% url reader_add_subscription %}',
									params: {
										'url': text,
										'csrfmiddlewaretoken': '{% with csrf_token as csrf_token_clean %}{{ csrf_token_clean }}{% endwith %}',
									},
									success: function() {
										self.application.subscription_store.reload();
									},
									failure: function() {
										alert('Unable to add feed.');
									},
								});
							}
						});
					},
				},'->',{
					text: 'Refresh',
					handler: function() {
						self.application.subscription_store.reload();
					},
				},
			],
			collapsible: true,
		}));
		
		listView.on('selectionchange', function(listView, selections) {
			if (selections.length > 0) {
				self.application.selected_subscription(listView.getSelectedRecords()[0]['data']);
			}
		});
	},
});


Reader.EntryPanel = Ext.extend(Ext.Panel, {
	constructor: function(application, config) {
		this.application = application;
		var self = this;
		
		var gridView = this.gridView = new Ext.grid.GridPanel({
			store: this.application.entry_store,
			columns: [
				{
					header: 'Title',
					dataIndex: 'title',
				},
				{
					header: 'Date',
					dataIndex: 'date',
				},
			],
			viewConfig: {
				forceFit: true,
			},
			sm: new Ext.grid.RowSelectionModel({singleSelect: true}),
			region: 'north',
			split: true,
			height: 200,
			minSize: 150,
			maxSize: 400,
		});
		
		var entryDetailTpl = this.entryDetailTpl = new Ext.Template(
			'<h1><a href="{link}" target="_blank">{title}</a></h1>',
			'<p style="font-size: smaller;">{date}</p>',
			'<p>{content}</p>'
		);
		
		var entryDetail = this.entryDetail = {
			id: 'entryDetail',
			region: 'center',
			bodyStyle: {
				background: 'white',
				padding: '7px',
				color: 'black',
			},
			preventBodyReset: true,
			html: 'Select an entry to view',
			autoScroll: true,
		};
		
		gridView.getSelectionModel().on('rowselect', function(sm, rowIdx, r) {
			var detailPanel = Ext.getCmp('entryDetail');
			entryDetailTpl.overwrite(detailPanel.body, r.data);
			
			Ext.Ajax.request({
				url: '{% url reader_read_entry %}',
				params: {
					'entry_id': r.data['id'],
					'csrfmiddlewaretoken': '{% with csrf_token as csrf_token_clean %}{{ csrf_token_clean }}{% endwith %}',
				},
				success: function() {
					self.application.subscription_store.reload();
				},
				failure: function() {
					console.log('Unable to set read entry');
				},
			});
		});
		
		Reader.EntryPanel.superclass.constructor.call(this, Ext.applyIf(config||{}, {
			title: 'Entries',
			header: true,
			items: [ this.gridView, this.entryDetail ],
			layout: 'border',
		}));
	},
});


Reader.Application = Ext.extend(Ext.util.Observable, {
	constructor: function(config) {
		Ext.apply(this, config, {
			renderTo: Ext.getBody(),
		});
		Reader.Application.superclass.constructor.call(this);
		this.init();
	},
	init: function() {
		Ext.QuickTips.init();
		
		var subscription_store = this.subscription_store = new Ext.data.JsonStore({
			autoLoad: true,
			autoDestroy: true,
			url: '{% url reader_get_subscriptions %}',
			root: 'root',
			totalProperty: 'len',
			fields: [
				'id',
				'title',
				'unread',
			]
		});
		
		var entry_store = this.entry_store = new Ext.data.JsonStore({
			url: '{% url reader_get_entries %}',
			baseParams: {
				'subscription_id': '-2',
				'csrfmiddlewaretoken': '{% with csrf_token as csrf_token_clean %}{{ csrf_token_clean }}{% endwith %}',
			},
			root: 'root',
			totalProperty: 'len',
			fields: [
				'id', 'title', 'date', 'content', 'link'
			],
		});
		
		var subscription_panel = this.subscription_panel = new Reader.SubscriptionPanel(this, {
			region: 'west',
			split: true,
			width: 200,
			minSize: 150,
			maxSize: 400,
		});
		var entry_panel = this.entry_panel = new Reader.EntryPanel(this, {
			region: 'center',
			autoScroll: true,
		});
		var viewport = this.viewport = new Ext.Viewport({
			layout: 'border',
			renderTo: this.renderTo,
			items: [
				this.subscription_panel,
				this.entry_panel,
			],
		});
		
		this.viewport.doLayout();
	},
	selected_subscription: function(subscription) {
		this.entry_panel.setTitle(subscription['title']);
		this.entry_store.reload({ params: {
			'subscription_id': subscription['id'],
		}});
	}
});