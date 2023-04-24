import json
import traceback
import tornado

import logging
_logger = logging.getLogger(__name__)

class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(self, env) -> None:
        self.env = env
        pass

    def write_error(self, status_code: int, **kwargs) -> None:
        self.set_header(
            'Content-Type', 'application/json; charset=UTF-8'
        )
        body = {
            'method': self.request.method,
            'uri': self.request.path,
            'code': status_code,
            'message': self._reason
        }
        if self.settings.get("serve_traceback") \
            and "exc_info" in kwargs:
            # in debug mode, send a traceback
            trace = '\n'.join(traceback.format_exception(
                *kwargs['exc_info']
            ))
            body['trace'] = trace
        self.finish(body)


class ControllerManagerListCreate(BaseRequestHandler):
    async def get(self, model_name):
        offset = self.get_argument('offset', 0)
        limit = self.get_argument('limit', 60)
        sort_fields = self.get_argument('sort_fields', None)
        if sort_fields and isinstance(sort_fields, str):
            sort_fields = [sf.strip() for sf in sort_fields.split(",")]       

        records = await self.env[model_name].list(offset=offset, limit=limit, sort_fields=sort_fields)
        self.set_status(200)
        self.finish(json.dumps({
            "items": json.dumps(records, default=vars),
            "total_items": len(self.env[model_name]),
        }))

    async def post(self, model_name):
        data = json.loads(self.request.body.decode('utf-8'))
        record = await self.env[model_name].create(data)
        self.set_status(201)
        # self.set_header('Location', addr_uri)
        self.finish(json.dumps(record, default=vars))
        
        # json.loads(self.request.body.decode('utf-8'))
        # try:
        #     _logger.info("Json request body: %s", str(self.request.body))            
        #     data = json.loads(self.request.body.decode('utf-8'))
        #     record = await self.env[model_name].create(data)
        #     self.set_status(201)
        #     # self.set_header('Location', addr_uri)
        #     self.finish(json.dumps(record))
        # except (json.decoder.JSONDecodeError, TypeError):
        #     raise tornado.web.HTTPError(
        #         400, reason='Invalid JSON body'
        #     ) from None
        # except ValueError as e:
        #     raise tornado.web.HTTPError(400, reason=str(e))

class ControllerManagerGetUpdateDelete(BaseRequestHandler):
    async def get(self, model_name, id):
        _logger.info("ControllerManagerGetUpdateDelete get %s %s", str(model_name), str(id))
        try:
            record = await self.env[model_name].get(id)
            self.set_status(200)
            self.finish(json.dumps(record, default=vars))
        except KeyError as e:
            raise tornado.web.HTTPError(404, reason=str(e))

    # async def put(self, id):
    #     try:
    #         addr = json.loads(self.request.body.decode('utf-8'))
    #         await self.service.update_address(id, addr)
    #         self.set_status(204)
    #         self.finish()
    #     except (json.decoder.JSONDecodeError, TypeError):
    #         raise tornado.web.HTTPError(
    #             400, reason='Invalid JSON body'
    #         )
    #     except KeyError as e:
    #         raise tornado.web.HTTPError(404, reason=str(e))
    #     except ValueError as e:
    #         raise tornado.web.HTTPError(400, reason=str(e))

    # async def delete(self, id):
    #     try:
    #         await self.service.delete_address(id)
    #         self.set_status(204)
    #         self.finish()
    #     except KeyError as e:
    #         raise tornado.web.HTTPError(404, reason=str(e))
