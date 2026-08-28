/**
 * Generated, do not edit. Regenerate with npm.cmd --prefix web run gen:types
 */

export interface paths {
    "/api/health": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Health */
        get: operations["health_api_health_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/fields": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Fields */
        get: operations["fields_api_fields_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/report": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        /** Report */
        get: operations["report_api_report_get"];
        put?: never;
        post?: never;
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/fields/{field_id}/preview": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Field Preview */
        post: operations["field_preview_api_fields__field_id__preview_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
    "/api/fields/{field_id}/value": {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        get?: never;
        put?: never;
        /** Field Value */
        post: operations["field_value_api_fields__field_id__value_post"];
        delete?: never;
        options?: never;
        head?: never;
        patch?: never;
        trace?: never;
    };
}
export type webhooks = Record<string, never>;
export interface components {
    schemas: {
        /** CheckModel */
        CheckModel: {
            /**
             * Status
             * @enum {string}
             */
            status: "ok" | "warn" | "fail";
            /** Name */
            name: string;
            /** Detail */
            detail: string;
        };
        /** FieldInfo */
        FieldInfo: {
            /** Id */
            id: string;
            /** Question */
            question: string;
            /** Unit */
            unit: string;
            /** Min */
            min: number;
            /** Max */
            max: number;
            /** File */
            file: string;
            /** Line */
            line: number;
            /** Current Value */
            current_value: unknown;
            /**
             * Status
             * @enum {string}
             */
            status: "measured" | "todo";
            /** Measurement Label */
            measurement_label: string | null;
            /** Group */
            group: string;
        };
        /** FieldsResponse */
        FieldsResponse: {
            /** Revision */
            revision: string;
            /** Fields */
            fields: components["schemas"]["FieldInfo"][];
        };
        /** HTTPValidationError */
        HTTPValidationError: {
            /** Detail */
            detail?: components["schemas"]["ValidationError"][];
        };
        /** HeadlineItem */
        HeadlineItem: {
            /** Label */
            label: string;
            /** Value */
            value: number | string;
            /** Unit */
            unit: string;
        };
        /** HealthResponse */
        HealthResponse: {
            /** Ok */
            ok: boolean;
            /** Project Root */
            project_root: string;
        };
        /** PreviewRequest */
        PreviewRequest: {
            /** Value */
            value: string | number;
        };
        /** PreviewResponse */
        PreviewResponse: {
            /** Diff */
            diff: string;
        };
        /** Report */
        Report: {
            /** Headline */
            headline: components["schemas"]["HeadlineItem"][];
            /** Checks */
            checks: components["schemas"]["CheckModel"][];
        };
        /** StaleRevisionResponse */
        StaleRevisionResponse: {
            /** Detail */
            detail: string;
            current: components["schemas"]["FieldsResponse"];
        };
        /** ValidationError */
        ValidationError: {
            /** Location */
            loc: (string | number)[];
            /** Message */
            msg: string;
            /** Error Type */
            type: string;
            /** Input */
            input?: unknown;
            /** Context */
            ctx?: Record<string, never>;
        };
        /** ValueWriteRequest */
        ValueWriteRequest: {
            /** Value */
            value: string | number;
            /** Revision */
            revision: string;
        };
        /** ValueWriteResponse */
        ValueWriteResponse: {
            result: components["schemas"]["WriteResultModel"];
            report: components["schemas"]["Report"];
            /** Revision */
            revision: string;
            /** Warnings */
            warnings: string[];
        };
        /** WriteResultModel */
        WriteResultModel: {
            /** File */
            file: string;
            /** Line Number */
            line_number: number;
            /** Old Text */
            old_text: string;
            /** New Text */
            new_text: string;
            /** Checklist Ticked */
            checklist_ticked: boolean;
        };
    };
    responses: never;
    parameters: never;
    requestBodies: never;
    headers: never;
    pathItems: never;
}
export type $defs = Record<string, never>;
export interface operations {
    health_api_health_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HealthResponse"];
                };
            };
        };
    };
    fields_api_fields_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["FieldsResponse"];
                };
            };
        };
    };
    report_api_report_get: {
        parameters: {
            query?: never;
            header?: never;
            path?: never;
            cookie?: never;
        };
        requestBody?: never;
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["Report"];
                };
            };
        };
    };
    field_preview_api_fields__field_id__preview_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                field_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["PreviewRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["PreviewResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
    field_value_api_fields__field_id__value_post: {
        parameters: {
            query?: never;
            header?: never;
            path: {
                field_id: string;
            };
            cookie?: never;
        };
        requestBody: {
            content: {
                "application/json": components["schemas"]["ValueWriteRequest"];
            };
        };
        responses: {
            /** @description Successful Response */
            200: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["ValueWriteResponse"];
                };
            };
            /** @description Conflict */
            409: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["StaleRevisionResponse"];
                };
            };
            /** @description Validation Error */
            422: {
                headers: {
                    [name: string]: unknown;
                };
                content: {
                    "application/json": components["schemas"]["HTTPValidationError"];
                };
            };
        };
    };
}
