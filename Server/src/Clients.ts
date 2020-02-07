export type Client = {
    username: string;
    client: object;
}

export type Clients = {
    [key:string] : Client;
}