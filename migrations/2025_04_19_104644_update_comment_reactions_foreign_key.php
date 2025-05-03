<?php

use Illuminate\Support\Facades\Schema;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Database\Migrations\Migration;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('comment_reactions', function (Blueprint $table) {
            // Xóa khóa ngoại cũ
            $table->dropForeign(['comment_id']);

            // Tạo lại với ON DELETE CASCADE
            $table->foreign('comment_id')
                  ->references('comment_id')
                  ->on('comments')
                  ->onDelete('cascade');
        });
    }

    public function down(): void
    {
        Schema::table('comment_reactions', function (Blueprint $table) {
            // Xóa khóa ngoại có cascade
            $table->dropForeign(['comment_id']);

            // Tạo lại KHÔNG cascade
            $table->foreign('comment_id')
                  ->references('comment_id')
                  ->on('comments');
        });
    }
};
