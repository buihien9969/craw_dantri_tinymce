<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class AddForeignKeyToModerationLogs extends Migration
{
    public function up()
    {
        Schema::table('moderation_logs', function (Blueprint $table) {
            $table->foreign('moderator_id')
                ->references('user_id')
                ->on('users')
                ->onDelete('cascade');
        });
    }

    public function down()
    {
        Schema::table('moderation_logs', function (Blueprint $table) {
            $table->dropForeign(['moderator_id']);
        });
    }
} 