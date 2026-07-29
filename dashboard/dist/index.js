(function () {
  "use strict";

  const SDK = window.__HERMES_PLUGIN_SDK__;
  const { React } = SDK;
  const { useState, useEffect, useCallback } = SDK.hooks;
  const {
    Card, CardHeader, CardTitle, CardContent,
    Badge, Button, Select, SelectOption, Separator,
  } = SDK.components;

  const MONTH_OPTIONS = [
    { value: "1", label: "Last 1 month" },
    { value: "2", label: "Last 2 months" },
    { value: "3", label: "Last 3 months" },
    { value: "4", label: "Last 4 months" },
    { value: "5", label: "Last 5 months" },
    { value: "6", label: "Last 6 months" },
    { value: "custom", label: "Custom Range" },
  ];

  function statusVariant(status) {
    const s = (status || "").toLowerCase();
    if (s.includes("done") || s.includes("closed") || s.includes("resolved")) return "secondary";
    if (s.includes("progress") || s.includes("review")) return "default";
    return "outline";
  }

  function TicketRow({ ticket }) {
    return React.createElement(
      "div",
      { className: "flex items-center justify-between py-3 gap-3" },
      React.createElement(
        "div",
        { className: "min-w-0 flex-1" },
        React.createElement(
          "div",
          { className: "flex items-center gap-2 flex-wrap" },
          React.createElement(
            "a",
            {
              href: ticket.url,
              target: "_blank",
              rel: "noopener noreferrer",
              className: "text-sm font-medium text-primary hover:underline",
              title: "Open in Jira",
            },
            ticket.key,
          ),
          React.createElement(Badge, { variant: statusVariant(ticket.status) }, ticket.status || "Unknown"),
          ticket.priority
            ? React.createElement(Badge, { variant: "outline" }, ticket.priority)
            : null,
        ),
        React.createElement(
          "p",
          { className: "text-sm text-muted-foreground truncate mt-1" },
          ticket.summary || "(no summary)",
        ),
      ),
      React.createElement(
        "div",
        { className: "text-xs text-muted-foreground whitespace-nowrap" },
        ticket.updated ? SDK.utils.isoTimeAgo(ticket.updated) : "",
      ),
    );
  }

  function MyJiraTicketsPage() {
    const [months, setMonths] = useState("1");
    const [statusFilter, setStatusFilter] = useState("all");
    const [startDate, setStartDate] = useState("");
    const [endDate, setEndDate] = useState("");
    const [page, setPage] = useState(1);
    const [tickets, setTickets] = useState([]);
    const total = tickets.length;
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const load = useCallback(() => {
      setLoading(true);
      setError(null);
      let url = `/api/plugins/hermes-jira-board/tickets?status=${encodeURIComponent(statusFilter)}`;
      if (months === "custom") {
        if (startDate && endDate) {
          url += `&start_date=${encodeURIComponent(startDate)}&end_date=${encodeURIComponent(endDate)}`;
        } else {
          url += `&months=1`;
        }
      } else {
        url += `&months=${months}`;
      }
      SDK.fetchJSON(url)
        .then((data) => {
          setTickets(data.issues || []);
        })
        .catch((err) => setError(err.message || String(err)))
        .finally(() => setLoading(false));
    }, [months, statusFilter, startDate, endDate]);

    useEffect(() => {
      load();
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    return React.createElement(
      Card,
      null,
      React.createElement(
        CardHeader,
        { className: "flex flex-row items-center justify-between gap-4" },
        React.createElement(CardTitle, null, "Hermes Jira Board"),
        React.createElement(
          "div",
          { className: "flex items-center gap-2" },
          React.createElement(
            Select,
            {
              value: months,
              onValueChange: setMonths,
              onChange: (e) => setMonths(e?.target ? e.target.value : e),
              "aria-label": "Time range",
            },
            MONTH_OPTIONS.map((o) =>
              React.createElement(SelectOption, { key: o.value, value: o.value }, o.label),
            ),
          ),
          React.createElement("input", {
            type: "text",
            list: "jira-common-statuses",
            placeholder: "Status (e.g. all, open, To Do)",
            value: statusFilter,
            onChange: (e) => setStatusFilter(e.target.value),
            className: "flex h-10 w-48 rounded-md border border-input bg-background px-3 py-2 text-sm",
            "aria-label": "Status filter",
          }),
          React.createElement(
            "datalist",
            { id: "jira-common-statuses" },
            React.createElement("option", { value: "all" }, "All statuses"),
            React.createElement("option", { value: "open" }, "Open only"),
            React.createElement("option", { value: "To Do" }),
            React.createElement("option", { value: "In Progress" }),
            React.createElement("option", { value: "In Review" }),
            React.createElement("option", { value: "Done" }),
          ),
          months === "custom" ? React.createElement("input", {
            type: "date",
            value: startDate,
            onChange: (e) => setStartDate(e.target.value),
            className: "flex h-10 w-36 rounded-md border border-input bg-background px-3 py-2 text-sm",
            "aria-label": "Start date",
          }) : null,
          months === "custom" ? React.createElement("span", { className: "text-sm text-muted-foreground" }, "to") : null,
          months === "custom" ? React.createElement("input", {
            type: "date",
            value: endDate,
            onChange: (e) => setEndDate(e.target.value),
            className: "flex h-10 w-36 rounded-md border border-input bg-background px-3 py-2 text-sm",
            "aria-label": "End date",
          }) : null,
          React.createElement(Button, { onClick: () => { setPage(1); load(); }, disabled: loading }, loading ? "Loading..." : "Apply Filters"),
        ),
      ),
      React.createElement(
        CardContent,
        null,
        error
          ? React.createElement(
              "p",
              { className: "text-sm text-destructive" },
              `Couldn't load tickets: ${error}`,
            )
          : null,
        !error && !loading && tickets.length === 0
          ? React.createElement(
              "p",
              { className: "text-sm text-muted-foreground" },
              "No tickets assigned to you in this window.",
            )
          : null,
        React.createElement(
          "div",
          { className: "divide-y divide-border" },
          tickets.slice((page - 1) * 10, page * 10).map((t) => React.createElement(TicketRow, { key: t.key, ticket: t })),
        ),
        total > 0 ? React.createElement(
          "div",
          { className: "flex items-center justify-between mt-4 pt-4 border-t border-border" },
          React.createElement("span", { className: "text-sm text-muted-foreground" }, `Showing ${Math.min((page - 1) * 10 + 1, total)} - ${Math.min(page * 10, total)} of ${total} tickets (Page ${page} of ${Math.max(1, Math.ceil(total / 10))})`),
          React.createElement(
            "div",
            { className: "flex gap-2" },
            React.createElement(Button, { variant: "outline", size: "sm", disabled: page <= 1 || loading, onClick: () => setPage(p => p - 1) }, "Previous"),
            React.createElement(Button, { variant: "outline", size: "sm", disabled: page * 10 >= total || loading, onClick: () => setPage(p => p + 1) }, "Next")
          )
        ) : null,
      ),
    );
  }

  window.__HERMES_PLUGINS__.register("hermes-jira-board", MyJiraTicketsPage);
})();
