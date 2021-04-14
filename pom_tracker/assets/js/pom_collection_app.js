// noinspection JSVoidFunctionReturnValueUsed

let pom_app = {};

Pom_Collection_App = function () {

    let Pomodoro = new function () {

        let Model = Backbone.Model.extend({
            defaults: {
                date: "",
                title: "",
                flags: "",
                start_time: "",
                end_time: "",
                distractions: "",
                pom_success: "",
                description: ""
            }
        });

        let Collection = Backbone.Collection.extend({

            model: Model,

            fetch: function () {

                let that = this;

                $.ajax({
                    url: "/pomodoro/get_collection",
                    type: "GET",
                    cache: false,
                    dataType: "json",
                    contentType: "application/json",

                    success: function (data, textStatus, jqXHR) {
                        // console.log(data);
                        that.set(that.parse(data.poms));
                        that.trigger("init:table", data.total_count);
                    },

                    error: function (jqXHR, textStatus, errorThrown) {
                        // console.log(jqXHR);
                        // console.log(textStatus);
                        // console.log(errorThrown);
                    }
                });
            },

            parse: function (data) {
                dataset = [];
                _.each(data, function (value, key) {
                    let flags = "";
                    _.each(value.flags, function (value, key) {
                        flags += (value + "<br>");
                    });
                    dataset.push(
                        {
                            date: value.created,
                            title: value.task,
                            flags: flags,
                            start_time: value.start_time,
                            end_time: value.end_time,
                            distractions: value.distractions,
                            pom_success: value.pom_success,
                            description: value.review
                        }
                    )
                });
                return dataset;
            },

            get_pomodoros: function () {
                return _.pluck(this.models, "attributes");
            }
        });

        let View = Backbone.View.extend({
            el: "#pom-table",

            tagName: "table",

            table: null,

            initialize: function () {

                this.table = this.$el.DataTable({
                    paging: false,
                    ordering: false,
                    info: false,
                    searching: false,
                    columns: [
                        {
                            data: "date",
                            title: "Date"
                        },
                        {
                            data: "title",
                            title: "Title"
                        },
                        {
                            data: "flags",
                            title: "Flags"
                        },
                        {
                            data: "start_time",
                            title: "Start Time"
                        },
                        {
                            data: "end_time",
                            title: "End Time"
                        },
                        {
                            data: "distractions",
                            title: "Distractions"
                        },
                        {
                            data: "pom_success",
                            title: "Pom Success"
                        },
                        {
                            data: "description",
                            title: "Description"
                        }
                    ]
                });
            },

            populate_table: function (pomodoros) {
                this.table.clear();
                this.table.rows.add(pomodoros);
                this.table.draw();
            }
        });

        this.Component = Backbone.View.extend({
            initialize: function () {
                this.model = new Model();
                this.collection = new Collection();
                this.view = new View();

                // Event Listeners
                this.listenTo(this.collection, 'init:table', this.init_table);
            },

            fetch: function () {
                this.collection.fetch();
            },

            init_table: function (total_count) {
                this.trigger('init:table', total_count);
            },

            populate_table: function (pomodoros) {
                this.view.populate_table(pomodoros);
            },

            get_pomodoros: function () {
                return this.collection.get_pomodoros();
            },

            set_collection: function (pomodoros) {
                pomodoros = this.collection.parse(pomodoros);
                this.collection.set(pomodoros);
            }
        });
    };

    let Filter = new function () {

        let Model = Backbone.Model.extend({

            defaults: {
                date_filter: "",
                unsuccessful_filter: false,
                distractions_filter: false
            },

            initialize: function () {
                this.on('change', this.on_model_change);
            },

            on_model_change: function () {
                this.trigger('change:model');
            },

            set_date_filter: function (value) {
                this.set("date_filter", value);
            },

            set_unsuccessful_filter: function () {
                let value = this.get("unsuccessful_filter");
                let toggle = !value;
                this.set("unsuccessful_filter", toggle);
            },

            set_distractions_filter: function () {
                let value = this.get("distractions_filter");
                let toggle = !value;
                this.set("distractions_filter", toggle);
            },

            get_filters: function () {
                return this.attributes;
            }
        });

        let View = Backbone.View.extend({
            el: "#filters",

            tagName: "div",

            events: {
                "change .date_filter": "onClickDateFilter",
                "click .unsuccessful_filter": "onClickSuccessFilter",
                "click .distractions_filter": "onClickDistractionsFilter"
            },

            onClickDateFilter: function (e) {
                this.trigger("filter:date", e.currentTarget.value);
            },

            onClickSuccessFilter: function () {
                this.trigger("filter:success");
            },

            onClickDistractionsFilter: function () {
                this.trigger("filter:distractions");
            }
        });

        this.Component = Backbone.View.extend({
            initialize: function () {
                this.model = new Model();
                this.view = new View();

                // Event Listeners
                this.listenTo(this.model, 'change:model', this.on_model_change);
                this.listenTo(this.view, "filter:date", this.set_date_filter);
                this.listenTo(this.view, "filter:success", this.set_unsuccessful_filter);
                this.listenTo(this.view, "filter:distractions", this.set_distractions_filter);
            },

            on_model_change: function () {
                this.trigger('change:model');
            },

            get_filters: function () {
                return this.model.get_filters();
            },

            set_date_filter: function (value) {
                this.model.set_date_filter(value);
            },

            set_unsuccessful_filter: function () {
                this.model.set_unsuccessful_filter();
            },

            set_distractions_filter: function () {
                this.model.set_distractions_filter();
            }
        });
    };

    let Pagination = new function () {

        var Model = Backbone.Model.extend({
            defaults: {
                limit: 20,
                offset: 0,
                total_record_count: 0
            },

            initialize: function () {
                this.on('change', this.on_model_change);
            },

            on_model_change: function () {
                this.trigger('change:model');
            },

            update_pagination_total: function (total_record_count) {
                this.set({total_record_count: total_record_count}, {silent: true});
            },

            set_offset: function (page_num) {
                // Calculate the offset based on the clicked link number an the limit
                var offset = (parseInt(page_num) - 1) * this.get('limit');

                this.set({
                    'limit': this.get('limit'),
                    'offset': offset
                });
            },

            get_pagination: function () {
                return this.attributes;
            },

            reset_pagination: function (silent) {
                if (silent) {
                    this.set(this.defaults, {silent: true});
                } else {
                    this.set(this.defaults);
                }
            }
        });

        var View = Backbone.View.extend({

            el: 'div.pagination',

            events: {
                'click a.pagination-offset-link': 'on_click_offset_link'
            },

            on_click_offset_link: function (e) {

                var disabled = $(e.currentTarget).parent('li').hasClass('disabled');

                if (!disabled) {
                    // Get the pagination link number so we can calculate the proper offset
                    var page_num = $(e.currentTarget).data('pagenum');

                    this.trigger('change:offset', page_num);
                }
            },

            update_offset_links: function (pagination) {
                var num_links = 5;
                var links = [];
                var num_pages = Math.ceil(pagination.total_record_count / pagination.limit);
                var current_page = Math.floor((pagination.offset / pagination.limit) + 1);

                // Hide the pagination links entirely when there are no records found
                if (pagination.total_record_count == 0) {
                    $('div.pagination').css('visibility', 'hidden');

                }
                // Show pagination links and initialize them
                else {
                    $('div.pagination').css('visibility', 'visible');

                    // Remove active class from all pagination links
                    $('div.pagination a.pagination-offset-link').each(function () {
                        $(this).parent('li').removeClass('active');
                    });

                    // Remove active class from all pagination links
                    $('div.pagination a.pagination-offset-link').each(function () {
                        $(this).parent('li').removeClass('active');
                    });

                    // Handle links when total records are <= 4 pages
                    if (num_pages <= 4) {
                        links = [1, 2, 3, 4];
                    }
                    // Calculate links for large data sets
                    else {

                        // Calculate pagination pages
                        if (current_page == 2 || current_page == (num_pages - 1)) {
                            links.push(current_page - 1);
                        } else if ((current_page > 2 && current_page < (num_pages - 1)) || current_page == num_pages) {
                            links.push(current_page - 2);
                            links.push(current_page - 1);
                        }

                        // Adjust num links if there were any added already
                        num_links = num_links - links.length;

                        // Set remaining pagination pages
                        for (var i = 0; i < num_links; i++) {
                            links.push(current_page + i);
                        }
                    }

                    // Set pagination offset links
                    for (var i in links) {
                        $('#offset' + (parseInt(i) + 1)).data('pagenum', links[i]);
                        $('#offset' + (parseInt(i) + 1)).text(links[i]);
                    }
                    $('#last').data('pagenum', num_pages);

                    this.handle_link_display(current_page, num_pages);

                    this.set_pagination_count_info(pagination);
                }
            },

            handle_link_display: function (current_page, num_pages) {

                if (num_pages <= 4) {
                    switch (num_pages) {
                        case 1:
                            $('#offset2').hide();
                            $('#offset3').hide();
                            $('#offset4').hide();
                            $('#offset5').hide();
                            break;
                        case 2:
                            $('#offset2').show();
                            $('#offset3').hide();
                            $('#offset4').hide();
                            $('#offset5').hide();
                            break;
                        case 3:
                            $('#offset2').show();
                            $('#offset3').show();
                            $('#offset4').hide();
                            $('#offset5').hide();
                            break;
                        case 4:
                            $('#offset2').show();
                            $('#offset3').show();
                            (current_page >= 3) ? $('#offset4').show() : $('#offset4').hide();
                            $('#offset5').hide();
                            break;
                        default:
                            break;
                    }
                    $('#offset' + current_page).parent('li').addClass('active');

                } else {
                    $('#offset2').show();
                    $('#offset3').show();

                    // Handle showing/hiding extra offset links and setting the active link
                    if (current_page > 2 && current_page < (num_pages - 1)) {
                        $('#offset4').show();
                        $('#offset5').show();
                        $('#offset3').parent('li').addClass('active');

                    } else {
                        if ([1, 2].indexOf(current_page) !== -1) {
                            $('#offset4').hide();
                            $('#offset5').hide();
                            $('#offset' + current_page).parent('li').addClass('active');

                        } else if (current_page == num_pages) {
                            $('#offset4').hide();
                            $('#offset5').hide();
                            $('#offset3').parent('li').addClass('active');

                        } else if (current_page == (num_pages - 1)) {
                            $('#offset4').hide();
                            $('#offset5').hide();
                            $('#offset2').parent('li').addClass('active');
                        }
                    }
                }
            },

            set_pagination_count_info: function (pagination) {
                var first_record_num = (pagination.offset + 1);
                var last_record_num = pagination.offset + pagination.limit;

                if (last_record_num > pagination.total_record_count) {
                    last_record_num = pagination.total_record_count;
                }

                var count_text = first_record_num + ' to ' + last_record_num + ' of ' + pagination.total_record_count;
                $('#pagination-count-info').text(count_text);
            }
        });

        this.Component = Backbone.View.extend({
            initialize: function () {
                this.model = new Model();
                this.view = new View();

                // Event Listeners
                this.listenTo(this.model, 'change:model', this.on_model_change);
                this.listenTo(this.view, 'change:offset', this.set_offset);
            },

            on_model_change: function () {
                this.trigger('change:model');
            },

            set_offset: function (page_num) {
                this.model.set_offset(page_num);
            },

            get_pagination: function () {
                return this.model.get_pagination();
            },

            reset_pagination: function (silent) {
                this.model.reset_pagination(silent);
                this.view.update_offset_links(this.get_pagination());
            },

            update_offset_links: function () {
                return this.view.update_offset_links(this.get_pagination());
            },

            update_pagination_total: function (total_record_count) {
                return this.model.update_pagination_total(total_record_count);
            }
        });
    };

    this.Application = Backbone.View.extend({

        initialize: function () {
            this.filters = new Filter.Component();
            this.pagination = new Pagination.Component();
            this.pomodoro = new Pomodoro.Component();

            this.listenTo(this.filters, "change:model", this.execute);
            this.listenTo(this.pagination, "change:model", this.execute);
            this.listenTo(this.pomodoro, "init:table", this.init_table);

            this.pomodoro.fetch();
        },

        init_table: function (total_count) {
            let pomodoros = this.pomodoro.get_pomodoros();
            this.pomodoro.populate_table(pomodoros);
            this.pagination.update_pagination_total(total_count);
            this.pagination.update_offset_links();
        },

        execute: function () {
            let that = this;
            let pagination = this.pagination.get_pagination();
            let filters = this.filters.get_filters();

            let data = {
                offset: pagination.offset,
                distractions_filter: filters.distractions_filter ? 1 : 0,
                unsuccessful_filter: filters.unsuccessful_filter ? 1 : 0
            };

            if (filters.date_filter) {
                data.date_filter = filters.date_filter;
            }

            $.ajax({
                url: "/pomodoro/get_collection",
                type: "GET",
                data: data,
                cache: false,
                dataType: "json",
                contentType: "application/json",

                success: function (data, textStatus, jqXHR) {
                    // console.log(data);
                    that.pomodoro.set_collection(data.poms);
                    that.init_table(data.total_count);
                },

                error: function (jqXHR, textStatus, errorThrown) {
                    // console.log(jqXHR);
                    // console.log(textStatus);
                    // console.log(errorThrown);
                }
            });
        }
    });

    pom_app = new Application();
}();
