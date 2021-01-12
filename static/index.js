$(function () {
    var data = [{
            action: "type",
            strings: ["pip install PyGithubBlog"],
            output: '<span class="gray">Successfully installed PyGithubBlog</span><br>&nbsp;',
            postDelay: 1000,
        },
        {
            action: "type",
            strings: ["gitblog"],
            output: '<span class="gray">PyGithubBlog created pages</span>&nbsp;',
            postDelay: 4000,
        },
    ];
    runScripts(data, 0);
});

function runScripts(data, pos) {
    var prompt = $(".prompt"),
        script = data[pos];
    if (script.clear === true) {
        $(".history").html("");
    }
    switch (script.action) {
        case "type":
            prompt.removeData();
            $(".typed-cursor").text("");
            prompt.typed({
                strings: script.strings,
                typeSpeed: 40,
                callback: function () {
                    var history = $(".history").html();
                    history = history ? [history] : [];
                    history.push(`$ ${prompt.text()}`);
                    if (script.output) {
                        history.push(script.output);
                        prompt.html("");
                        $(".history").html(history.join("<br>"));
                    }
                    $("section.terminal").scrollTop($("section.terminal").height());
                    pos++;
                    if (pos < data.length) {
                        setTimeout(function () {
                            runScripts(data, pos);
                        }, script.postDelay || 1000);
                    }
                },
            });
            break;
        case "view":
            break;
    }
}

$("input#flexSwitchCheckDefault").change(function () {
    var container = document.getElementsByClassName("container")[0];
    if ($(this).is(":checked")) {
        document.body.style.background = "#111827";
        container.getElementsByTagName("h1")[0].style.color = "#f9fafb";
        container.getElementsByTagName("h3")[0].style.color = "#f9fafb";
        container.getElementsByTagName("p")[0].style.color = "#f9fafb";
        $(this).css("background-color", "#111827");
    } else {
        document.body.style.background = "#f9fafb";
        container.getElementsByTagName("h1")[0].style.color = "#111827";
        container.getElementsByTagName("h3")[0].style.color = "#111827";
        container.getElementsByTagName("p")[0].style.color = "#6b7280";
        $(this).css("background-color", "#f9fafb");
    }
});