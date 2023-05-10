import { DEVMODE } from './globals'
import { UID } from './main'

let SERVER_LOG_ROOT = DEVMODE ? "http://127.0.0.1:5000/" : "https://zouharvi.pythonanywhere.com/"
let SERVER_DATA_ROOT = DEVMODE ? "http://127.0.0.1:9000/queues/" : "queues/"

export async function load_data(): Promise<any> {
    let result = await $.getJSON(
        "baked_queues/" + UID + ".json",
    )
    return result
}
export async function log_data(data): Promise<any> {
    console.log(data)
    console.log(globalThis.url_data)
    data["url_data"] = globalThis.url_data

    console.log(data)

    let result = await $.ajax(
        SERVER_LOG_ROOT + "log",
        {
            data: JSON.stringify({
                project: "image-complexity",
                uid: globalThis.uid,
                payload: JSON.stringify(data),
            }),
            type: 'POST',
            contentType: 'application/json',
        }
    )
    return result
}