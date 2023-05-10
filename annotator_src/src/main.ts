import { DEVMODE } from "./globals"
export var UID: string
import { load_data, log_data } from './connector'
import { shuffle_array } from './utils'

var data: any[] = []
let curr = -1
let prev_time = Date.now()

$("#button_next").on("click", () => {
    if (curr != -1) {
        let time = Date.now() - prev_time
        let config = data[curr]["config"]
        let logged_data = { id: data[curr]["id"], time: time, config: config }

        //"counting", "caption", "detection", "completion", "shuffle"
        if (config == "caption") {
            logged_data['caption'] = $("#caption_val").val()
            logged_data['confidence'] = $("#cap_confidence").val()
        } else if (config == "counting") {
            logged_data['count'] = $("#counting_val").val()
            logged_data['confidence'] = $("#count_confidence").val()
        } else if (config == "detection") {
            let answer = $("#check_y").is(":checked");
            logged_data['answer'] = answer
            if (answer == false && !$("#check_n").is(":checked")) logged_data['answer'] = 'none'
            logged_data['confidence'] = $("#det_confidence").val()
        } else if (config == "completion") {
            logged_data['description'] = $("#completion_val").val()
            logged_data['confidence'] = $("#comp_confidence").val()
        } else if (config == "shuffle"){
            $("#grid").css("grid-template-columns", "60% 40%")
            let res = new Array<[number, number]>();
            let positions = new Array<JQueryCoordinates>()
            let targetPos = $("#shuffle-0").position()
            for (let i = 0; i < 4; i++) {
                for (let j = 0; j < 4; j++) {
                    let pos = $(`#shuffle-${i*4+j}`).position()
                    console.log(pos)
                    positions.push(pos);
                    if (pos.left < targetPos.left || pos.top < targetPos.top)
                        targetPos = pos;
                    // console.log("posI: %f, posJ %f, left %f, top %f", posI, posJ, pos.left, pos.top);
                }
            }
            console.log(targetPos);
            for (let i = 0; i < 4; i++) {
                for (let j = 0; j < 4; j++) {
                    let pos = positions[i*4+j]
                    let posI = (pos.left - targetPos.left)/100;
                    let posJ = (pos.top - targetPos.top)/100;
                    console.log("posI: %f, posJ %f, left %f, top %f", posI, posJ, pos.left, pos.top);
                    res.push([posI, posJ])
                    $(`#shuffle-${i*4+j}`).remove()
                }
            }
            console.log(res);
        } else {
            console.log("Error unkown mode")
        }
        console.log(logged_data)
        log_data(logged_data)
    }
    next_image()
});

$('.range').on('input change', function () {
    $(".range_text").text($(this).val()!.toString())
});


$('input[type="checkbox"]').on('change', function () {
    $('input[name="' + this.name + '"]').not(this).prop('checked', false);
});

function show_mode(config: string) {
    // cleanup previous data
    $("#caption_val").html("")
    $("#counting_val").html("")
    $("#completion_val").html("")
    $(".range_text").text("-")

    $("#caption_box").hide();
    $("#counting_box").hide();
    $("#shuffle_box").hide();
    $("#shuffle_dummy").hide();
    $("#detection_box").hide();
    $("#completion_box").hide();

    // default is normal image box
    $("#image_box_shuffle").hide()
    $("#image_box_shuffle_target").hide()
    $("#image_box").show()

    if (config == "caption") {
        $("#caption_box").show();
    } else if (config == "completion") {
        $("#completion_box").show();
    } else if (config == "counting") {
        $("#counting_box").show();
    } else if (config == "detection") {
        $("#detection_box").show();
    } else if (config == "shuffle") {
        $("#shuffle_box").show();
        $("#shuffle_dummy").show();
        $("#image_box_shuffle").show()
        $("#image_box_shuffle_target").show()
        $("#image_box").hide()
    }
}

function next_image() {
    curr += 1
    if (curr >= data.length) {
        alert("Annotations done, please wait a few seconds after closing this alert to allow for data synchronization.")
        curr = 0
    }

    let config = data[curr]["config"]

    $("#config_info").html("Mode: " + config)

    show_mode(config)

    if (config == "shuffle") {
        $("#answer_box").css({"left":"300px"}).animate({"left":"0px"}, "slow");
    }
    if (config == "shuffle") {
        let fragments_all = new Array<string>()
        for(let i = 0; i < 4; i++) {
            for(let j = 0; j < 4; j++) {
                fragments_all.push(`
                    <div shuffle_pos_i=${i} shuffle_pos_j=${j} id="shuffle-${i*4+j}" class="draggable_fragment ui-widget-content">
                        <img style="margin-left: ${-j*100}px; margin-top: ${-i*100}px" src='data/original_images/${data[curr]['id']}'>
                    </div>
                `)
            }
        }

        let fragments_grid = new Array<string>()
        for (let i = 0; i < 4; i++) {
            for (let j = 0; j < 4; j++) {
                fragments_grid.push(`
                    <div class="grid_fragment"></div>
                `)
            }
        }

        fragments_all = shuffle_array(fragments_all)
        $("#image_box_shuffle").html(fragments_all.join("\n")).queue( () => {
            // activate draggability
            // we need  to wait/queue for the DOM event loop
            if (!DEVMODE)
                $("#button_next").prop("disabled", true);
            console.log("Hello from DOM loader!")
            // @ts-ignore
            $(".draggable_fragment").draggable({
                grid: [100, 100],
                containment: $("#grid"),
                stop: function (event, ui) {
                    var position = $("#image_box_shuffle").position();
                    var rightBorder = position.left + 400
                    var done = true
                    for (var i = 0; i < 4; i++) {
                        for (var j = 0; j < 4; j++) 
                        {
                            var elementPos = $(`#shuffle-${i*4+j}`).position()
                            if (elementPos.left < rightBorder) {
                                done = false;
                                break;
                            }
                        }
                        if (!done) {
                            break
                        }
                    }
                    if (done) {
                        $("#button_next").prop("disabled", false);
                    }
                }
            });
            $("#image_box_shuffle").dequeue();
            

        });

        $("#image_box_shuffle_target").html(fragments_grid.join("\n"))

        $("#grid").css("grid-template-columns", "50% 50%")
    } else if (config == "completion") {
        $("#image_box").html("<img src='data/cropped_images/" + data[curr]["id"] + "'>")
    } else {
        $("#image_box").html("<img src='data/original_images/" + data[curr]["id"] + "'>")
    }



    prev_time = Date.now()
    update_progress()
}

function update_progress() {
    $("#progress").text((curr + 1).toString() + "/" + (data.length).toString())
}

// get user id and load queue

// try to see if start override was passed
const urlParams = new URLSearchParams(window.location.search);
const startOverride = urlParams.get('start');
const UIDFromURL = urlParams.get("uid")

console.log(DEVMODE)

if (UIDFromURL != null) {
    globalThis.uid = UIDFromURL as string
} else if (DEVMODE) {
    globalThis.uid = "demo"
    UID = "demo"
} else {
    let UID_maybe: any = null
    while (UID_maybe == null) {
        UID_maybe = prompt("Enter your user id. Please get in touch if you were not assigned an id but wish to participate in this experiment.")
    }
    globalThis.uid = UID_maybe!
}

load_data().catch((_error) => {
    alert("Invalid user id")
    window.location.reload()
}
).then((new_data) => {
    data = new_data
    if (startOverride != null) {
        curr = parseInt(startOverride) - 1
        console.log("Starting from", curr)
    }
})

console.log("Starting session with UID:", globalThis.uid!)
show_mode("none")