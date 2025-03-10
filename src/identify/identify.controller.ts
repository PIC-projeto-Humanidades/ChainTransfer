/*
https://docs.nestjs.com/controllers#controllers
*/
import { Response } from 'express';

import { Controller, Get, Res } from '@nestjs/common';

@Controller("device")
export class IdentifyController {

    @Get('id')
    async getDeviceId(@Res() res: Response){
        const device = "node-a";
        res.status(200).json({id: device});
    }
}
